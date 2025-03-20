from django.conf import settings
from rest_framework import serializers
from users.models import User, UserApiUsage
import stripe
#
# class GoogleAuthResponseSerializer(serializers.Serializer):
#     sub = serializers.CharField()
#     email = serializers.EmailField()
#     email_verified = serializers.BooleanField()
#     name = serializers.CharField()
#     picture = serializers.URLField()
#     given_name = serializers.CharField()
#     family_name = serializers.CharField(required=False)
#



class UserDetailSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()
    subscriptions_detail = serializers.SerializerMethodField()
    token_usage = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'subscriptions', 'subscriptions_detail', 'token_usage')

    def get_subscriptions(self, obj):
        if obj.user_subscription:
            return obj.user_subscription.is_active
        return False

    def get_subscriptions_detail(self, obj):
        if obj.user_subscription:
            if obj.user_subscription.is_active:
                stripe.api_key = settings.STRIPE_API_KEY
                subscription = stripe.Subscription.retrieve(obj.user_subscription.stripe_subscription_id)
                return subscription
        return {}

    def get_token_usage(self, obj):
        api_usage = UserApiUsage.objects.filter(user=obj).first()
        if api_usage:
            return {
                'total_limit': api_usage.total_limit,
                'product': api_usage.product,
                'remaining_limit': api_usage.remaining_limit,
            }
        return None
