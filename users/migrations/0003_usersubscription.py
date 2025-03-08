# Generated by Django 5.1.6 on 2025-03-08 10:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_options_user_date_joined_user_groups_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSubscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("stripe_customer_id", models.CharField(max_length=255, unique=True)),
                (
                    "stripe_subscription_id",
                    models.CharField(max_length=255, unique=True),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_subscription",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
