from django.conf import settings
from django.http.response import JsonResponse
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from common.response_mixins import BaseAPIView
from rest_framework_simplejwt.tokens import RefreshToken
import stripe
from users.models import User, UserSubscription
from users.serializers import UserDetailSerializer
from users.utils import validate_google_token
from rest_framework.permissions import IsAuthenticated

class GoogleLoginView(BaseAPIView, CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.filter().first()

            refresh = RefreshToken.for_user(user)
            return self.send_success_response(
                message="Login successful",
                data={
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            )


            access_token = request.data.get("access_token")

            if access_token:
                # Validate the access token before fetching profile data
                token_info = validate_google_token(access_token)

                if not token_info:
                    return self.send_bad_request_response(
                        message="Invalid or expired access token."
                    )

                if token_info and token_info.get("email"):
                    user = User.objects.filter(email=token_info["email"]).first()
                    if not user:
                        name = token_info["name"].split(" ", 1)
                        user = User.objects.create_user(
                            first_name=name[0],
                            last_name=name[1] if len(name) > 1 else "",
                            email=token_info["email"],
                            password=None,  # Don't set a hardcoded password
                        )

                    refresh = RefreshToken.for_user(user)
                    return self.send_success_response(
                        message="Login successful",
                        data={
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    )
                else:
                    return self.send_bad_request_response(
                        message="Email permission is not granted or email is not available."
                    )
            else:
                return self.send_bad_request_response(
                    message="No access token provided."
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

class StripeProductListing(BaseAPIView, ListAPIView):
    permission_classes = []
    queryset = None
    serializer_class = None

    def list(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            products = stripe.Product.list(limit=10)  # Fetch up to 10 products
            return self.send_success_response(data=products)

        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class StripeSubscriptionCheckout(BaseAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = None

    def create(self, request, *args, **kwargs):
        try:
            # Stripe product price ID (create in Stripe Dashboard)
            product_id = request.data.get("product_id")
            stripe.api_key =settings.STRIPE_API_KEY
            if not product_id:
                return self.send_bad_request_response(message="No product id provided.")
            prices = stripe.Price.list(product=product_id, limit=1)
            price_id = prices['data'][0]['id']
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",  # Subscription mode
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
                metadata={"user_id": request.user.id},
            )
            return self.send_success_response(data=checkout_session.url)

        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class StripeWebhookView(BaseAPIView, CreateAPIView):
    permission_classes = []
    queryset = None
    serializer_class = None

    def create(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Handle subscription confirmation
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session["metadata"].get("user_id")  # Retrieve user ID from metadata
            stripe_customer_id = session["customer"]
            stripe_subscription_id = session["subscription"]

            # Ensure user exists
            user = User.objects.get(id=user_id)
            # Store subscription details in the database
            UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    "stripe_customer_id": stripe_customer_id,
                    "stripe_subscription_id": stripe_subscription_id,
                    "is_active": True,
                }
            )

        return JsonResponse({"status": "success"}, status=200)

class UserDetailView(BaseAPIView, RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = UserDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        return self.send_success_response(data=serializer.data)