from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username=None, email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            if not email:
                raise ValueError(_('The email or username must be set'))

        if email:
            email = self.normalize_email(email)

            if not username:
                username = email

            user = self.model(
                username=username,
                email=email,
                **extra_fields,
            )
        
        # elif phone:
        #     if not username:
        #         username = phone
        #     user = self.model(
        #         username=username,
        #         email=False,
        #         phone=phone,
        #         **extra_fields,
        #     )

        # проверяем является ли пользователь
        # суперпользователем
        if extra_fields.get('is_superuser'):
            user = self.model(
                username=username,
                **extra_fields
            )
        
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(
            username=username, 
            email=email,
            password=password, 
            **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(
            username=username,
            password=password,
            email=email,
            **extra_fields
        )