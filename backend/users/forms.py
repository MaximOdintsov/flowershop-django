from django.contrib.auth import authenticate, get_user_model, password_validation

from django.utils.translation import gettext_lazy as _

from django import forms
from django.contrib.auth import forms as forms_auth

from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()


class MyRegistrationForm(forms_auth.UserCreationForm):
    YEARS = [x for x in range(1940, 2022)]
    SEX_CHOICES = [
        ('N', 'Не выбран'),
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
    ]
    error_messages = {
        'required': 'Это поле обязательно для заполнения',
    }

    username = forms.CharField(
        label=_('Username'),
        min_length=4,
        max_length=254,
        error_messages=error_messages,
    )
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        error_messages=error_messages,
    )
    first_name = forms.CharField(
        label=_('First name'),
        error_messages=error_messages
    )
    last_name = forms.CharField(
        label=_('Last name'),
        error_messages=error_messages
    )
    sex = forms.TypedChoiceField(
        label=_('Sex'),
        choices=SEX_CHOICES,
        required=False
    )
    date_of_birth = forms.DateField(
        label=_('Day of Birth'),
        initial='1990-01-01',
        widget=forms.SelectDateWidget(years=YEARS),
    )

    def clean_username(self):
        new_username = self.cleaned_data['username'].lower()
        existing = User.objects.filter(username=new_username)

        if existing:
            raise ValidationError(f'Такое имя пользователя уже есть. Выберите другое.')
        return new_username

    def clean_email(self):
        new_email = self.cleaned_data.get('email').lower()
        existing = User.objects.filter(email=new_email)

        if existing:
            raise ValidationError(f'Пользователь с таким адресом электронной почты уже существует.')
        return new_email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        # user = super(RegistrationForm, self).save(commit=False)
        user = User.objects.create(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            sex=self.cleaned_data['sex'],
            date_of_birth=self.cleaned_data['date_of_birth'],
            password=self.cleaned_data['password2'],
        )
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta(forms_auth.UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )
        field_classes = {
            'username': forms_auth.UsernameField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ваш email',
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ваше имя',
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ваша фамилия',
        })

        self.fields['sex'].widget.attrs.update({
            'class': 'form-select',
            'placeholder': 'Выберите пол',
        })
        self.fields['date_of_birth'].widget.attrs.update({
            'class': 'form-select col-md-4',
            'style': 'margin-right: calc(var(--bs-gutter-x) * .5)',
            'placeholder': 'Дата рождения',
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })


class MyAuthenticationForm(forms_auth.AuthenticationForm):
    username = forms_auth.UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True
    }))

    error_messages = {
        'invalid_login': 'Введены неверные данные для авторизации.',
        'inactive': 'Почта не была подтверждена.',
    }

    class Meta:
        model = User
        fields = ['email', 'password']

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(MyAuthenticationForm, self).__init__(request, *args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя или email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })


class MyPasswordResetForm(forms_auth.PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control',
            'placeholder': 'Введите адрес электронной почты',
        }),
    )

    def clean_email(self):
        new_email = self.cleaned_data.get('email').lower()
        existing = User.objects.filter(email=new_email)

        if not existing:
            raise ValidationError(f'Пользователя с таким адресом электронной почты не существует.\n'
                                  f'Проверьте правильность написания')
        return new_email


class MySetPasswordForm(forms_auth.SetPasswordForm):

    new_password1 = forms.CharField(
        label=_("New password"),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
        }),
    )

    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль',
        }),
    )


class MyPasswordChangeForm(forms_auth.PasswordChangeForm):

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'Введите старый пароль',
            }
        ),
    )
    new_password1 = forms.CharField(
        label=_('New password'),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
        }),
    )
    new_password2 = forms.CharField(
        label=_('New password confirmation'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль',
        }),
    )

    def __int__(self, request=None, *args, **kwargs):
        self.request = request
        super(MyPasswordChangeForm, self).__init__(request, *args, **kwargs)

        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите старый пароль',
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль',
        })

