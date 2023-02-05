from django.urls import path

from .views import ProductList, ProductFilterView, ProductSearchView, ProductDetailView


urlpatterns = [
    path('', ProductList.as_view(), name='product_list'),
    path('products/filter', ProductFilterView.as_view(), name='product_filter'),
    path('products/search', ProductSearchView.as_view(), name='product_search'),
    path('products/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
]
