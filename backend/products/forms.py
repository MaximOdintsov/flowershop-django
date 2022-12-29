from django import forms


from .models import ProductCategory


class ProductSearchForm(forms.Form):
    search_text = forms.CharField(

        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control me-1 c-bg-input c-light',
                'placeholder': 'Введите название товара',
            }
        ),
    )


class ProductFilterForm(forms.Form):
    categories = ProductCategory.objects.all()
    CATEGORY_CHOICES = [
        (category.id, category.title) for category in categories
    ]

    PRICE_CHOICE = [
        ('A', 'Сначала дешевле'),
        ('D', 'Сначала дороже')
    ]

    category = forms.MultipleChoiceField(
        label='Категории продуктов',
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check-input',
                'placeholder': 'Выберите категорию',
            }
        ),
    )

    price = forms.TypedChoiceField(
        label='Цена',
        choices=PRICE_CHOICE,
        required=False,
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input',
            }
        ),
    )