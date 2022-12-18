from django.urls import path, include

from .views import OrderCreateView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order_create'),
]