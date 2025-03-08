from django.contrib import admin

from users.models import User, UserSubscription

admin.site.register(User)
admin.site.register(UserSubscription)
