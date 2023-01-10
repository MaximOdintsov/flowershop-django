from django.urls import path

from .views import (AddItemToCart,
                    AddOneItemToCart,
                    RemoveItemToCart,
                    RemoveOneItemToCart,
                    cart_view,
                    OrderCreateView,
                    OrderCreatedView)

urlpatterns = [
    # path('add-item-to-cart/<int:pk>', add_item_to_cart, name='add_item_to_cart'),
    path('cart/add_item_to_cart/<int:pk>', AddItemToCart.as_view(), name='add_item_to_cart'),
    path('cart/add_one_item_to_cart/<int:pk>', AddOneItemToCart.as_view(), name='add_one_item_to_cart'),

    path('cart/remove_item_to_cart/<int:pk>', RemoveItemToCart.as_view(), name='remove_item_to_cart'),
    path('cart/remove_one_item_to_cart/<int:pk>', RemoveOneItemToCart.as_view(), name='remove_one_item_to_cart'),

    path('cart/', cart_view, name='cart'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('created/', OrderCreatedView.as_view(), name='order_created'),
]