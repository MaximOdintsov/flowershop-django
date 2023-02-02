from django.db.models import Q

from django.contrib.auth import get_user_model

User = get_user_model()


class AuthBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, request, username, password):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
        except User.DoesNotExist:
            return None

        if user and user.check_password(password):
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
           return User.objects.get(pk=user_id)
        except User.DoesNotExist:
           return None