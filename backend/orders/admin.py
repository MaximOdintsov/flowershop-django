from django.contrib import admin
from . import models
from django.db import transaction


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    fields = ('product', 'quantity')


@admin.register(models.Order)
class Order(admin.ModelAdmin):
    fields = ('user', 'receipt_method', 'payment_method', 'payment_state', 'order_status', 'readiness_status')

    list_display = ['creation_time', 'readiness_status', 'order_status', 'first_name', 'phone', 'address',
                    'amount', 'receipt_method', 'payment_state', 'payment_method', 'order_on_site']
    list_editable = ['order_status', 'readiness_status', 'payment_state', 'payment_method', 'receipt_method']
    inlines = [OrderItemInline, ]

    @transaction.atomic
    def delete_queryset(self, request, queryset):
        """
        Переопределение действия 'Удалить выбранные объекты'
        """
        orders = queryset
        for order in orders:
            order.delete()
