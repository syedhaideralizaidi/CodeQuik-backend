from django.db.models import (
    CharField,
    ForeignKey,
    CASCADE,
    IntegerField,
    TextField,
    BooleanField,
    DateTimeField,
    OneToOneField,
)
# from api.utils.model_utils import Timestamp
# from api.organisation.models import Organisation
from subscription.choices import PACKAGE
from django.utils.translation import gettext_lazy as _

from utils.model_utils import Timestamp
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class Subscription(Timestamp):
    user = OneToOneField(
        User, on_delete=CASCADE, related_name="user_in_subscription"
    )
    monthly_price = IntegerField(default=0)
    yearly_price = IntegerField(default=0)
    subscription_id = CharField(max_length=100, null=True, blank=True)
    package = CharField(max_length=25, choices=PACKAGE, default="MonthlyPro")
    start = DateTimeField(null=True, blank=True)
    end = DateTimeField(null=True, blank=True)
    status = CharField(max_length=100, null=True, blank=True)
    cancel_at = DateTimeField(null=True, blank=True)
    last_payment = DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")


class TransactionHistory(Timestamp):
    user = ForeignKey(User, on_delete=CASCADE)
    description = TextField(null=True, blank=True)
    success = BooleanField(default=False)
    amount = IntegerField(default=0)
    charge_id = CharField(max_length=256, null=True, blank=True)
    reason = CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = _("transaction History")
        verbose_name_plural = _("transactions History")
