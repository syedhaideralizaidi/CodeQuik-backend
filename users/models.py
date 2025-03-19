from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser


class UserManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    password = models.CharField(max_length=128, null=True, blank=True)
    first_name = models.CharField(max_length=512, blank=True, null=True)
    last_name = models.CharField(max_length=512, blank=True, null=True)
    full_name = models.CharField(max_length=512, blank=True, null=True)
    email = models.EmailField('email address', unique=True)
    username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []



class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_subscription')  # Each user has one subscription
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.stripe_subscription_id}"

class UserApiUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='api_usage')
    total_limit = models.PositiveIntegerField(default=1000)
    product = models.CharField(max_length=255)
    remaining_limit = models.PositiveIntegerField(default=1000)


class UserTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_transaction')
    amount = models.FloatField()
    product = models.CharField(max_length=255)