from django.urls import path, re_path, include
# from django.contrib.auth.urls import views
from .views import (
    MyRegistrationView,
    MyLoginView,
    MyPasswordResetView,
    MyPasswordResetConfirmView,
    MyPasswordChangeView,
    VerifyEmail,
    EmailConfirmation,
    EmailConfirmationInvalid,
    EmailConfirmationDone,
)

# for reading static files
from django.conf import settings

urlpatterns = [

    path('login/', MyLoginView.as_view(), name='login'),
    path('registration/', MyRegistrationView.as_view(), name='registration'),
    path('password_change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', MyPasswordResetView.as_view(), name='password_reset'),
    path(
        "reset/<uidb64>/<token>/",
        MyPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path(
        'verify_email/<uidb64>/<token>/',
        VerifyEmail.as_view(),
        name="verify_email",
    ),
    path(
        'email_confirmation/',
        EmailConfirmation.as_view(),
        name='email_confirmation',
    ),
    path(
        'email_confirmation_done/',
        EmailConfirmationDone.as_view(),
        name='email_confirmation_done',
    ),
    path(
        'email_confirmation_invalid/',
        EmailConfirmationInvalid.as_view(),
        name='email_confirmation_invalid',
    ),


    path('', include('django.contrib.auth.urls')),

    # path('api/v1/auth/', include('djoser.urls')),
    # re_path(r'^auth/', include('djoser.urls.authtoken')),
]