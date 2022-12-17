from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from django import views
from django.views import generic
from django.contrib.auth import views as auth_views
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as token_generator

from .utils import send_email_for_verify

from .forms import (
    MyRegistrationForm,
    MyAuthenticationForm,
    MyPasswordResetForm,
    MySetPasswordForm,
    MyPasswordChangeForm,
)

from django.contrib.auth import get_user_model


User = get_user_model()


class MyRegistrationView(views.View):

    template_name = 'registration/registration.html'

    def get(self, request):
        context = {
            'form': MyRegistrationForm
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = MyRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2')

            user = authenticate(username=username, password=password)

            send_email_for_verify(request, user)

            return redirect('email_confirmation')
        else:
            return render(request, self.template_name, context={'form': form})


class VerifyEmail(views.View):

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if (user is not None) and (token_generator.check_token(user, token)):
            user.is_verified = True
            user.save()
            login(request, user)

            return redirect('email_confirmation_done')
        return redirect('email_confirmation_invalid')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user


class EmailConfirmation(generic.TemplateView):
    template_name = 'registration/email_confirmation.html'


class EmailConfirmationDone(generic.TemplateView):
    template_name = 'registration/email_confirmation_done.html'


class EmailConfirmationInvalid(generic.TemplateView):
    template_name = 'registration/email_confirmation_invalid.html'


class MyLoginView(auth_views.LoginView):
    form_class = MyAuthenticationForm
    success_url = 'home'


class MyPasswordResetView(auth_views.PasswordResetView):
    form_class = MyPasswordResetForm


class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = MySetPasswordForm


class MyPasswordChangeView(auth_views.PasswordChangeView):
    form_class = MyPasswordChangeForm



# class PasswordResetConfirmView(django_views.PasswordResetConfirmView):
#     post_reset_login = True


# class View(django_views.LoginView, SignUpView):
#     template_name = 'products/flower_list.html'
#
#     def get(self, request, **kwargs):
#         context = {
#             'login_form': AuthenticationForm,
#             'registration_form': SignUpForm,
#         }
#
#         return render(request, self.template_name, context=context)
#
#     def post(self, request, **kwargs):
#         login_form = AuthenticationForm
#         registration_form = SignUpForm
#
#         if login_form.is_valid():
#             django_views.LoginView.form_valid()
#
#         if registration_form.is_valid():
#             registration_form.save()
#             return redirect('home')
#
#         context = {
#             'login_form': AuthenticationForm,
#             'registration_form': SignUpForm,
#         }
#
#         return render(request, self.template_name, context=context)


# class MultipleFormsDemoView(MultiFormsView):
#     template_name = "pages/cbv_multiple_forms.html"
#     form_classes = {'contact': ContactForm,
#                     'subscription': SubscriptionForm,
#                     }
#
#     success_urls = {
#         'contact': reverse_lazy('contact-form-redirect'),
#         'subscription': reverse_lazy('submission-form-redirect'),
#     }
#
#     def contact_form_valid(self, form):
#         'contact form processing goes in here'
#
#     def subscription_form_valid(self, form):
#         'subscription form processing goes in here'
