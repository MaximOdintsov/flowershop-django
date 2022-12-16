from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'background-color: rgb(243, 243, 243);',
                'placeholder': 'Количество',
            }
        )
    )

    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

