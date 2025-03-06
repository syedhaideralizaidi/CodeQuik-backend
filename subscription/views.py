import datetime

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from subscription.models import TransactionHistory, Subscription
from subscription.serializers import CreateCheckoutSessionSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateUserCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validate request data (the 'plan' should be one of "Pro", "Pro50", or "Pro100")
        serializer = CreateCheckoutSessionSerializer(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data.get("plan")
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Map each plan to a Stripe price configuration (adjust these settings accordingly)
        if plan == "Pro":
            price_item = settings.STRIPE_PRO_PRICE  # e.g. {"price": "price_1XYZ...", "quantity": 1}
        elif plan == "Pro50":
            price_item = settings.STRIPE_PRO50_PRICE
        elif plan == "Pro100":
            price_item = settings.STRIPE_PRO100_PRICE
        else:
            return Response({"message": "Invalid plan selected."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a Stripe checkout session for a subscription
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=request.user.email,  # optionally use existing customer id if available
            line_items=[{
                "price": price_item.get("price"),
                "quantity": price_item.get("quantity", 1),
            }],
            client_reference_id=request.user.id,  # useful for later reference
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={
                "plan": plan,
                "user_id": request.user.id,
            },
        )

        return Response({"session_id": checkout_session.id}, status=status.HTTP_200_OK)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        # Invalid payload or invalid signature
        return HttpResponse(status=400)

    # Handle the checkout session completion event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        plan = metadata.get("plan")
        stripe_subscription_id = session.get("subscription")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(status=400)

        # Create or update the Subscription record for the user
        Subscription.objects.update_or_create(
            user=user,
            defaults={
                "subscription_id": stripe_subscription_id,
                "package": plan,
                "start": datetime.datetime.fromtimestamp(session["created"]),
                "status": "active",
                # You can update monthly/yearly pricing here if needed
            }
        )

        # Log the transaction history (if needed)
        TransactionHistory.objects.create(
            user=user,
            description="Subscription created via Stripe Checkout",
            success=True,
            amount=session.get("amount_total", 0),  # adjust based on your needs (e.g. convert cents to dollars)
            charge_id=stripe_subscription_id,
        )

    # Handle other event types if necessary

    return HttpResponse(status=200)