from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from django import views
from django.contrib.auth import views as auth_views

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
            return redirect('home')

            # user = authenticate(
            #     username=email,
            #     password=password,
            # )

            # if user is not None:
            #     if user.is_active:
            #         login(self.request, user)
            #         return HttpResponse('Вы успешно вошли')
            #     else:
            #         return HttpResponse('Ваш аккаунт неактивен')
            # else:
            #     return HttpResponse('Такого юзера нет')

            # user = authenticate(username=username, password=password)
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return render(request, self.template_name, context={'form': form})


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
