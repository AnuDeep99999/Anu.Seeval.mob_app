from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class CustomUserBackend(BaseBackend):
    model = get_user_model()

    def authenticate(self, request=None, username=None, password=None):
        try:
            user = self.model.objects.get(email=username)
            if user.check_password(password):
                print("Password matching")
                return user
        except self.model.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.model.objects.get(pk=user_id)
        except self.model.DoesNotExist:
            return None
