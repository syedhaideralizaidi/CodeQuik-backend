from django.contrib import admin

from users.models import User, UserSubscription, UserApiUsage, UserTransaction

admin.site.register(User)
admin.site.register(UserSubscription)
admin.site.register(UserApiUsage)
admin.site.register(UserTransaction)
