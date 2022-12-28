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


@admin.register(ProductCategory)
class ProductCategory(admin.ModelAdmin):
    fields = ('title', 'slug')


@admin.register(ProductComponent)
class ProductComponent(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {
            'widget': forms.TextInput(attrs={'size': 10})
        },
    }
    prepopulated_fields = {"slug": ("title",)}

    fields = ('title', 'slug', 'price', 'total_count')
    list_display = ['title', 'price', 'new_arrival', 'total_count', 'quantity_in_product',
                    'quantity_for_sale', 'quantity_of_sold', 'available']
    list_editable = ['price', 'new_arrival', 'available']

    list_per_page = 40
    ordering = ['quantity_of_sold', 'price']


@admin.register(Product)
class Product(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {
            'widget': forms.TextInput(attrs={'size': 10})
        },
    }
    inlines = [ProductGalleryInline, ProductCompositionInline]

    fields = ('category', 'title', 'slug', 'preview', 'discount', 'status')
    list_display = ['title', 'category', 'discount', 'new_price', 'quantity', 'status']
    list_editable = ['category', 'discount', 'quantity', 'status']

    list_per_page = 40


# class ProductGalleryInline(admin.TabularInline):
#     model = ProductGallery
#     extra = 0
#
#
# class ProductCompositionInline(admin.TabularInline):
#     model = ProductComposition
#     extra = 0
#     fields = ('component_composition', 'quantity', )
#     actions = ['save_composition', ]
#
#
# @admin.register(ProductCategory)
# class ProductCategory(admin.ModelAdmin):
#     fields = ('title', )
#
#
# @admin.register(ProductComponent)
# class ProductComponent(admin.ModelAdmin):
#     formfield_overrides = {
#         models.DecimalField: {
#             'widget': forms.TextInput(attrs={'size': 10})
#         },
#     }
#
#     fields = ('title', 'price',
#               'total_count', 'status')
#     list_display = ['title', 'price', 'new_arrival', 'total_count',
#                     'quantity_in_product', 'quantity_for_sale', 'available',
#                     'status']
#     list_editable = ['price', 'new_arrival', 'available', 'status']
#
#     list_per_page = 30
#     ordering = ['status', 'available', 'price']
#
#     @transaction.atomic
#     @admin.action(description='Удалить выбранные объекты')
#     def delete_queryset(self, request, queryset):
#         # переопределяем метод delete в actions
#         components = queryset
#         for component in components:
#             component.delete()
#
#
# @admin.register(Product)
# class Product(admin.ModelAdmin):
#     formfield_overrides = {
#         models.DecimalField: {
#             'widget': forms.TextInput(attrs={'size': 10})
#         },
#     }
#
#     inlines = [ProductGalleryInline, ProductCompositionInline, ]
#
#     fields = ('category', 'title', 'preview',
#               'status')
#     list_display = ['title', 'category', 'discount', 'discount_price',
#                     'quantity', 'available', 'status']
#     list_editable = ['category', 'discount', 'quantity', 'available', 'status']
#
#     list_per_page = 30
#     ordering = ['status', ]
#
#     actions = ['save_composition', ]
#
#     @transaction.atomic
#     def delete_queryset(self, request, queryset):
#         """
#         Переопределение действия 'Удалить выбранные объекты'
#         """
#         products = queryset
#         for product in products:
#             product.delete()
#
#         self.message_user(
#             request,
#             f'Было удалено {len(products)} продуктов'
#         )
#
#     @transaction.atomic
#     @admin.action(description='Обновить значения')
#     def save_composition(self, request, queryset):
#         # обновляем ProductComponent.quantity_in_product
#         # и рассчитываем ProductComponent.quantity_for_sale
#         products = queryset
#         for product in products:
#             product.save()
#
#         self.message_user(
#             request,
#             f'Было обновлено {len(products)} продуктов'
#         )
