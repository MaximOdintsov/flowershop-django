from django.urls import path

from . import views


urlpatterns = [
    path('', views.ProductList.as_view(), name='product_list'),
    path('products/filter', views.ProductFilterView.as_view(), name='product_filter'),
    path('products/search', views.ProductSearchView.as_view(), name='product_search'),
    # path('products/<slug:slug>', views.product_detail, name='product_detail'),

]
