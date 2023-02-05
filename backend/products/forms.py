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
    try:
        categories = ProductCategory.objects.filter(show_in_filter=True)
        if categories:
            CATEGORY_CHOICES = [
                (category.id, category.title) for category in categories
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
    except Exception:
        print(Exception)

    PRICE_CHOICE = [
        ('A', 'Сначала дешевле'),
        ('D', 'Сначала дороже')
    ]

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