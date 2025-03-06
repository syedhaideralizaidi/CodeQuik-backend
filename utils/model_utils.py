from django.db.models import DateTimeField, Model, CharField, fields
from django.utils.translation import gettext_lazy as _


class Timestamp(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self._meta.fields:
            if isinstance(field, CharField) and field.default is fields.NOT_PROVIDED:
                field.default = ""

    updated_at = DateTimeField(
        auto_now=True,
        editable=False,
    )
    created_at = DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = _("timestamp")
        verbose_name_plural = _("timestamps")
        abstract = True
