from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddBouquetForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=0,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
        })

    )

    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
