from django.contrib import admin
from django.db import models, transaction

from .models import (ProductCategory,
                     ProductComponent,
                     Product,
                     ProductGallery,
                     ProductComposition)

from django.contrib import admin

from django import forms


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 0


class ProductCompositionInline(admin.TabularInline):
    model = ProductComposition
    extra = 0
    fields = ('component', 'quantity')
    ordering = ('component', )


@admin.register(ProductCategory)
class ProductCategory(admin.ModelAdmin):
    fields = ('title', )
    list_display = ['title', 'slug', 'show_in_filter']
    list_editable = ['slug', 'show_in_filter']


@admin.register(ProductComponent)
class ProductComponent(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {
            'widget': forms.TextInput(attrs={'size': 10})
        },
    }
    fields = ('title', 'price', 'quantity_in_stock', 'show_in_filter')
    list_display = ['title', 'slug', 'price', 'new_arrival', 'quantity_in_stock',
                    'quantity_of_sold', 'available', 'show_in_filter']
    list_editable = ['price', 'slug', 'new_arrival', 'available', 'show_in_filter']

    list_per_page = 100
    ordering = ['title']


@admin.register(Product)
class Product(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {
            'widget': forms.TextInput(attrs={'size': 10})
        },
    }
    inlines = [ProductGalleryInline, ProductCompositionInline]

    fields = ('category', 'title', 'preview', 'discount', 'status', 'header_title', 'header_description')
    list_display = ['title', 'slug', 'category', 'discount', 'new_price', 'status']
    list_editable = ['category', 'slug', 'discount', 'status']

    list_per_page = 100
