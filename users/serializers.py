from rest_framework import serializers
from users.models import User
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
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'subscriptions')

    def get_subscriptions(self, obj):
        if obj.user_subscription:
            return obj.user_subscription.is_active
        return False
