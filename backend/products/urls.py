from django.urls import path

from . import views

# for reading static files
from django.conf import settings
from django.urls import include
from django.conf.urls.static import static

urlpatterns = [
    path('contacts', views.contacts, name='contacts'),
    path('', views.ProductList.as_view(), name='product_list'),
    path('products/<slug:slug>', views.product_detail, name='product_detail'),

]

# узнать, что такое as_view()