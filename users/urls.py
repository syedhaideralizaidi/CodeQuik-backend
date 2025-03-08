from django.urls import path

from users.views import GoogleLoginView, StripeProductListing, StripeSubscriptionCheckout, StripeWebhookView, \
    UserDetailView

# from .views import google_login

urlpatterns = [
    path("auth/google-login/", GoogleLoginView.as_view(), name="google_login"),
    path("stripe_product_listing", StripeProductListing.as_view(), name="stripe_product_listing"),
    path("stripe_subscription", StripeSubscriptionCheckout.as_view(), name="stripe_subscription"),
    path("stripe_webhook", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("user_detail", UserDetailView.as_view(), name="stripe_webhook"),
]