from django import forms


class ProductFilterForm(forms.Form):
    search_text = forms.CharField(
        label='Введите название продукта',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите название продукта',
            }
        ),
    )

