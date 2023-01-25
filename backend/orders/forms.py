from django import forms
from .models import Order, OrderItem
from phonenumber_field.formfields import PhoneNumberField

from django import forms


class AddQuantityForm(forms.Form):
    # PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]
    # PRODUCT_QUANTITY_CHOICES = [i for i in range(1, 21)]

    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-group rounded-0 border-0 text-center col-4 m-0',
                'style': 'background-color: rgb(243, 243, 243);',
                'placeholder': 'Количество',
            }
        )
    )
#
# class AddQuantityForm(forms.ModelForm):
#     # PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]
#     class Meta:
#         model = OrderItem
#         fields = ['quantity']


class OrderCreateForm(forms.ModelForm):

    error_messages = {
        'required': 'Это поле обязательно для заполнения',
    }

    RECEIPT_CHOICES = [
        (1, 'Самовывоз'),
        (2, 'Доставка курьером'),
    ]
    PAYMENT_CASH = 1
    PAYMENT_CARD = 2
    PAYMENT_TRANSFER = 3
    PAYMENT_ONLINE = 4
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Оплата наличными'),
        (PAYMENT_CARD, 'Оплата картой'),
        (PAYMENT_TRANSFER, 'Перевод на карту'),
        (PAYMENT_ONLINE, 'Онлайн оплата')
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
    # email = forms.EmailField(
    #     label='Электронная почта для отправки чека',
    #     min_length=1,
    #     error_messages=error_messages,
    #     required=False,
    #     widget=forms.EmailInput(
    #         attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Электронная почта для отправки чека',
    #         }
    #     ),
    # )
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
    receipt_method = forms.TypedChoiceField(
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
