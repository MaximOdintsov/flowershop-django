from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', )


@admin.register(Order)
class Order(admin.ModelAdmin):
    fields = ('user', 'first_name',
              'phone', 'email', 'address',
              'paid', 'readiness_status', 'receipt', 'payment_method')

    list_display = ['id', 'first_name', 'phone', 'address',
                    'price', 'receipt', 'paid', 'received', 'readiness_status']
    list_editable = ['paid', 'received', 'readiness_status']
    list_filter = ['readiness_status']
    inlines = [OrderItemInline, ]
