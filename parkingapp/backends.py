from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from .models import UserProfiles
class UserProfileBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = UserProfiles.objects.get(email=username)
            if user.check_password(password):
                return user
        except UserProfiles.DoesNotExist:
            return None
