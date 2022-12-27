import time

from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

from django.utils.translation import gettext_lazy as _
# from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):

    SEX_CHOICES = [
        ('N', 'Не выбран'),
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
    ]

    email = models.EmailField(_('Email'), unique=True)
    # phone = PhoneNumberField(_('phone number'), region='RU', unique=True, null=True, blank=True)
    sex = models.CharField('Пол', max_length=1, choices=SEX_CHOICES, null=True, blank=True,
                           default='N')
    date_of_birth = models.DateField('День рождения', null=True, blank=True)
    is_verified = models.BooleanField('Пользователь верифицирован', default=False,
                                      help_text='Указывает, что пользователь подтвердил свой email')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        unique_together = ('username', 'email')

    def __str__(self):
        return self.first_name

