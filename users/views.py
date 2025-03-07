from rest_framework.generics import CreateAPIView
from common.response_mixins import BaseAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.utils import validate_google_token


class GoogleLoginView(BaseAPIView, CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            access_token = request.data.get("access_token")

            if access_token:
                # Validate the access token before fetching profile data
                token_info = validate_google_token(access_token)

                if not token_info:
                    return self.send_bad_request_response(
                        message="Invalid or expired access token."
                    )

                if token_info and token_info.get("email"):
                    user = User.objects.filter(email=token_info["email"]).first()
                    if not user:
                        name = token_info["name"].split(" ", 1)
                        user = User.objects.create_user(
                            first_name=name[0],
                            last_name=name[1] if len(name) > 1 else "",
                            email=token_info["email"],
                            password=None,  # Don't set a hardcoded password
                        )

                    refresh = RefreshToken.for_user(user)
                    return self.send_success_response(
                        message="Login successful",
                        data={
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    )
                else:
                    return self.send_bad_request_response(
                        message="Email permission is not granted or email is not available."
                    )
            else:
                return self.send_bad_request_response(
                    message="No access token provided."
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))