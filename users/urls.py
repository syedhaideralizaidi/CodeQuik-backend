from django.urls import path

from users.views import GoogleLoginView

# from .views import google_login

urlpatterns = [
    path("auth/google-login/", GoogleLoginView.as_view(), name="google_login"),
]