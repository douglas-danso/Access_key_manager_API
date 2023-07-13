# backend.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from tryapp.models import CustomUser

class GoogleAuthBackend(ModelBackend):
    def authenticate(self, request, id_token):
        try:
            # Verify the Google ID token
            id_info = id_token.verify_oauth2_token(id_token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            # Check if the email is already registered in your system
            user = CustomUser.objects.get(email=id_info['email'])
        except CustomUser.DoesNotExist:
            # Create a new user account
            user = CustomUser.objects.create_user(email=id_info['email'])
        
        return user

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
