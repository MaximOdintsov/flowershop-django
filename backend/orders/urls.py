from django.urls import path
from django.views.generic import TemplateView
from .views import (AddItemToCart,
                    AddOneItemToCart,
                    RemoveItemToCart,
                    RemoveOneItemToCart,
                    cart_view,
                    OrderCreateView)

urlpatterns = [
    # path('add-item-to-cart/<int:pk>', add_item_to_cart, name='add_item_to_cart'),
    path('delivery_and_payment/', TemplateView.as_view(template_name='orders/delivery_and_payment.html'), name='delivery_and_payment'),
    path('cart/add_item_to_cart/<int:pk>', AddItemToCart.as_view(), name='add_item_to_cart'),
    path('cart/add_one_item_to_cart/<int:pk>', AddOneItemToCart.as_view(), name='add_one_item_to_cart'),

    path('cart/remove_item_to_cart/<int:pk>', RemoveItemToCart.as_view(), name='remove_item_to_cart'),
    path('cart/remove_one_item_to_cart/<int:pk>', RemoveOneItemToCart.as_view(), name='remove_one_item_to_cart'),

    path('cart/', cart_view, name='cart'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('created/', TemplateView.as_view(template_name='orders/order_created.html'), name='order_created'),
]