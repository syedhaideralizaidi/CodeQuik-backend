# # views.py
# from .serializers import GoogleAuthResponseSerializer
# from django.contrib.auth import get_user_model
# import logging
# import shortuuid
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.generics import GenericAPIView
# from django.contrib.auth.base_user import BaseUserManager
# from django.contrib.auth.hashers import make_password
# from rest_framework.response import Response
# import requests
# from rest_framework import status
# from django.db import transaction
# from django.conf import settings
#
# logger = logging.getLogger(__file__)
# User = get_user_model()
#
# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#     }
# def create_username(email):
#     # You can use your own logic too for creating the username
#     try:
#         total_retries = 5
#         email_split = email.rsplit(
#             "@", 1
#         )
#         email_part = email_split[0][0:20]
#         clean_email_part = "".join(char for char in email_part if char.isalnum())
#         for i in range(0, total_retries):
#             uuid = shortuuid.uuid()  # returns a 22 length alphanumeric string
#             username = (
#                 f"{clean_email_part}_{uuid}".lower()
#             )
#             existing_user = User.objects.filter(
#                 username=username
#             )
#             if existing_user.exists():
#                 continue
#             else:
#                 return username
#         raise Exception("Max retries done for creating a new username.")
#     except Exception as e:
#         raise Exception("Error while creating a new username") from e
# class GoogleAuthView(GenericAPIView):
#     response_serializer_class = UserLoginSerializer
#     def post(self, request):
#         try:
#             response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
#                 "Authorization": f"Bearer {request.data.get('token')}"
#             })
#             response_data = response.json()
#             logger.info("response from verify_oauth2_token", extra={"response_data": response_data})
#             if 'error' in response_data:
#                 logger.error("Wrong google token / this google token is already expired.", exc_info=True)
#                 return Response({
#                     "status": "error",
#                     "message": "Wrong google token / this google token is already expired.",
#                     "payload": {}
#                 }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception:
#             logger.error("Unexpected error occurred while hitting google auth api for authenticating the user", exc_info=True)
#             return Response({
#                 "status": "error",
#                 "message": "Unexpected error occurred, contact support for more info",
#                 "payload": {}
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         google_response_serializer = GoogleAuthResponseSerializer(data=response_data)
#         if google_response_serializer.is_valid() is False:
#             logger.error("Unexpected data received from google while authenticating the user.", exc_info=True)
#             return Response({
#                 "status": "error",
#                 "message": "Unexpected error occurred, contact support for more info",
#                 "payload": {}
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         validated_data = google_response_serializer.validated_data
#         email = validated_data['email'].lower()
#         given_name = validated_data["given_name"]
#         family_name = validated_data.get("family_name", "")
#         picture = validated_data.get("picture")
#         # Verify the Google Client ID
#         if validated_data['aud'] != settings.GOOGLE_CLIENT_ID:
#             logger.error("received aud not equivalent to the ", exc_info=True)
#             return Response({
#                 "status": "error",
#                 "message": "Invalid Token",
#                 "payload": {}
#             }, status=status.HTTP_400_BAD_REQUEST)
#         is_new_user = False
#         with transaction.atomic():
#             # create user if not exist
#             user = User.objects.filter(email=email).first()
#             if user is None:
#                 is_new_user = True
#                 username = create_username(email)
#                 # provider random default password
#                 password = make_password(BaseUserManager().make_random_password())
#                 user = User.objects.create_user(
#                     username=username, password=password, email=email, first_name=given_name, last_name=family_name,
#                     extras={"google_avatar_url": picture}
#                 )
#             if user.is_active is False:
#                 user.is_active = True
#                 user.save()
#             if user.google_auth_enabled is False:
#                 user.google_auth_enabled = True
#                 user.save()
#         serializer_data = self.response_serializer_class(
#             user, context={"request": request}
#         )
#         return Response(
#             data={
#                 "status": "success",
#                 "message": "Login Successful",
#                 "payload": serializer_data.data,
#                 "token": get_tokens_for_user(user),
#             },
#             status=status.HTTP_201_CREATED,
#         )