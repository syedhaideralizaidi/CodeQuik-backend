from rest_framework import serializers

from subscription.choices import PACKAGE
from subscription.models import Subscription


class CreateCheckoutSessionSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=PACKAGE, default="Pro")

    def validate(self, attrs):
        user = (
            self.context["request"].user
        )
        if Subscription.objects.filter(user=user).exists():
            raise serializers.ValidationError({"message": "Already Subscribed!"})
        return attrs