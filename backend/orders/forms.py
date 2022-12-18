from django import forms
from .models import Order
from phonenumber_field.formfields import PhoneNumberField


class OrderCreateForm(forms.ModelForm):

    error_messages = {
        'required': 'Это поле обязательно для заполнения',
    }

    RECEIPT_CHOICES = [
        (1, 'Самовывоз'),
        (2, 'Доставка курьером'),
    ]
    PAYMENT_CHOICES = [
        (1, 'Наличные'),
        (2, 'Безналичные'),
        (3, 'Онлайн оплата'),
    ]

    first_name = forms.CharField(
        label='Ваше имя',
        min_length=1,
        max_length=50,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
            }
        ),
    )
    phone = PhoneNumberField(
        label='Номер телефона',
        region='RU',
        error_messages=error_messages,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Номер телефона',
            }
        ),
    )
    email = forms.EmailField(
        label='Электронная почта для отправки чека',
        min_length=1,
        error_messages=error_messages,
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Электронная почта для отправки чека',
            }
        ),
    )
    address = forms.CharField(
        label='Адрес получателя',
        min_length=1,
        error_messages=error_messages,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Адрес получателя',
            }
        ),
    )
    receipt = forms.TypedChoiceField(
        error_messages=error_messages,
        choices=RECEIPT_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input',
            }
        ),
    )
    payment_method = forms.TypedChoiceField(
        label='Способ оплаты',
        error_messages=error_messages,
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input',
            }
        ),
    )

    class Meta:
        model = Order

        fields = ['first_name',
                  'phone', 'email', 'address']

    def save(self, user, commit=True, *args, **kwargs):

        order = Order.objects.create(
            user_id=args[0],
            first_name=self.cleaned_data['first_name'],
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email'],
            address=self.cleaned_data['address'],
            receipt=self.cleaned_data['receipt'],
            payment_method=self.cleaned_data['payment_method'],
        )
        order.save()


