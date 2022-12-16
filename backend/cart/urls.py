from django.urls import re_path, path
from .views import (
    cart_detail,
    cart_add_all,
    cart_remove_all,
    cart_add_one,
    cart_remove_one,
)


app_name = 'cart'

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<product_id>/', cart_add_all, name='cart_add_all'),
    path('add_one/<product_id>/', cart_add_one, name='cart_add_one'),
    path('remove/<product_id>/', cart_remove_all, name='cart_remove_all'),
    path('remove_one/<product_id>/', cart_remove_one, name='cart_remove_one'),
]