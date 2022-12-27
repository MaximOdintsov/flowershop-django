from django.contrib import admin
from . import models
from django.db import transaction


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    fields = ('product', 'quantity')


@admin.register(models.Order)
class Order(admin.ModelAdmin):
    fields = ('user', 'receipt_method', 'payment_method', 'order_status', 'readiness_status')

    list_display = ['creation_time', 'readiness_status', 'first_name', 'phone', 'address',
                    'amount', 'receipt_method', 'payment_method', 'order_status']
    list_editable = ['order_status', 'readiness_status']
    inlines = [OrderItemInline, ]

    @transaction.atomic
    def delete_queryset(self, request, queryset):
        """
        Переопределение действия 'Удалить выбранные объекты'
        """
        orders = queryset
        for order in orders:
            order.delete()



# class OrderItemInline(admin.TabularInline):
#     model = models.OrderItem
#     extra = 0
#     fields = ('product', 'quantity', )
#
#
# @admin.register(models.Order)
# class Order(admin.ModelAdmin):
#     fields = ('user', 'first_name',
#               'phone', 'email', 'address',
#               'paid', 'readiness_status', 'receipt', 'payment_method')
#
#     list_display = ['id', 'first_name', 'phone', 'address',
#                     'price', 'receipt', 'paid', 'received', 'readiness_status']
#     list_editable = ['paid', 'received', 'readiness_status']
#     list_filter = ['readiness_status']
#     inlines = [OrderItemInline, ]
#
#     @transaction.atomic
#     def delete_queryset(self, request, queryset):
#         """
#         Переопределение действия 'Удалить выбранные объекты'
#         """
#         orders = queryset
#         for order in orders:
#             order.delete()


