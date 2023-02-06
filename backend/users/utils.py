from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage

from django.contrib.auth.forms import PasswordResetForm


def send_email_for_verify(request, user):
    current_site = get_current_site(request)
    email_template_name = 'registration/verify_email.html'
    use_https = True
    shop_name = 'флористический салон Цветок'
    email_for_questions = 'questions@kirovcvetok.ru'

    context = {
        'user': user,
        'shop_name': shop_name,
        'email_for_questions': email_for_questions,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
        'protocol': 'https' if use_https else 'http',
    }
    message = render_to_string(
        email_template_name,
        context=context,
    )
    email = EmailMessage(
        'Подтверждение почты',
        message,
        to=[user.email],
    )
    email.send()