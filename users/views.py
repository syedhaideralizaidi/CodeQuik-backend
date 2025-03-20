from django.conf import settings
from django.http.response import JsonResponse
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from common.response_mixins import BaseAPIView
from rest_framework_simplejwt.tokens import RefreshToken
import stripe
from users.models import User, UserSubscription, UserTransaction, UserApiUsage
from users.serializers import UserDetailSerializer
from users.utils import validate_google_token, get_token_limit
from rest_framework.permissions import IsAuthenticated

class GoogleLoginView(BaseAPIView, CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            access_token = request.data.get("access_token")
            # print(access_token)
            # user = User.objects.filter().first()
            #
            # refresh = RefreshToken.for_user(user)
            # return self.send_success_response(
            #     message="Login successful",
            #     data={
            #         "refresh": str(refresh),
            #         "access": str(refresh.access_token),
            #     },
            # )
            #
            #
            #

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
                        user = User.objects.create(
                            full_name=token_info.get('name', None),
                            email=token_info["email"],
                            password=None,  # Don't set a hardcoded password
                        )
                        user_api_usage, created = UserApiUsage.objects.get_or_create(
                            user=request.user,
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
            enriched_products = []

            for product in products['data']:
                # Fetch prices for each product
                prices = stripe.Price.list(product=product['id'], limit=1)  # Adjust limit if multiple prices needed

                # Attach the first price if available
                product['price'] = prices['data'][0] if prices['data'] else None

                # Append the enriched product
                enriched_products.append(product)

            return self.send_success_response(data=enriched_products)

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


class StripeWebhookView(CreateAPIView):
    permission_classes = []
    queryset = None
    serializer_class = None

    def create(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY
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

            # Fetch subscription details
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            price_id = subscription["items"]["data"][0]["price"]["id"]

            # Fetch product details
            price = stripe.Price.retrieve(price_id)
            price_value = subscription["items"]["data"][0]["price"]['unit_amount'] / 100
            product_id = price["product"]
            product = stripe.Product.retrieve(product_id)
            product_name = product["name"]  # Get product name

            # Ensure user exists
            user = User.objects.get(id=user_id)
            UserTransaction.objects.create(
                user=user,
                amount = price_value,
                product = product_name,
            )
            api_limit = get_token_limit(product_name)
            UserApiUsage.objects.update_or_create(
                user=user,  # This is the lookup field to match an existing record
                defaults={
                    'total_limit': api_limit,
                    'remaining_limit': api_limit,
                }
            )
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


class UserApiUsageView(BaseAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = UserDetailSerializer

    def create(self, request, *args, **kwargs):
        token_count = request.data.get('token_count')
        if not isinstance(token_count, int):
            return self.send_bad_request_response(message="Token count must be an integer.")
        user_api_usage, created = UserApiUsage.objects.get_or_create(
            user=request.user,
        )
        if user_api_usage.remaining_limit < token_count:
            return self.send_bad_request_response(message="User can't have token limit. Not enough remaining tokens.")

            # Deduct tokens and save
        user_api_usage.remaining_limit -= token_count
        user_api_usage.save()

        # Optionally return remaining limit or success message
        return self.send_success_response(message="Tokens deducted successfully.", data={
            "remaining_limit": user_api_usage.remaining_limit
        })

class CancelStripeSubscription(BaseAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = None

    def create(self, request, *args, **kwargs):
        try:
            stripe.api_key = 'sk_test_51PNWpDBld7c7zRyojkuiogUHdGAm71dm01vCVs5vLb6lUIq2hUb75FOetDeYF5PVcZosungflo7yrbqiD8Yc09qb00tDyVWgvw'
            user = request.user
            if user.user_subscription:
                subscription_id = user.user_subscription.stripe_subscription_id
                stripe.Subscription.delete(subscription_id)
                user.user_subscription.is_active = False
                user.user_subscription.save()
                api_usage = UserApiUsage.objects.filter(user=user).first()
                if api_usage:
                    api_usage.remaining_limit = 1000
                    api_usage.total_limit = 100
                    api_usage.save()
                return self.send_success_response(message="Subscription cancelled.")
            return self.send_bad_request_response(message="Subscription can't be cancelled.")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))
