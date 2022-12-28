# from django.db.models import Q
# from django.shortcuts import render, get_object_or_404, redirect
# from django.views import generic
# from django import views
# from django.contrib.postgres.search import TrigramDistance, SearchVector
#
# from .models import Product, ProductCategory
# from .forms import ProductSearchForm, ProductFilterForm
#
# from cart.forms import CartAddProductForm
# from cart.cart import Cart
#
#
# class ProductFilterView(generic.ListView):
#     """Фильтрация товаров"""
#
#     model = Product
#     context_object_name = 'products'
#
#     cart_product_form = CartAddProductForm()
#     search_form = ProductSearchForm()
#     filter_form = ProductFilterForm()
#
#     extra_context = {
#         'cart_product_form': cart_product_form,
#         'search_form': search_form,
#         'filter_form': filter_form,
#     }
#
#     def get_queryset(self):
#
#         if self.request.GET.get('price') == 'A':
#             price = 'discount_price'
#         elif self.request.GET.get('price') == 'D':
#             price = '-discount_price'
#
#         query = Q(available=True) & (Q(status=2) | Q(status=3))
#
#         if self.request.GET.get('category'):
#             if self.request.GET.get('price'):
#                 products = Product.objects.filter(
#                     query,
#                     category__in=self.request.GET.get('category'),
#                 ).order_by(price)
#             else:
#                 products = Product.objects.filter(
#                     query,
#                     category__in=self.request.GET.get('category')
#                 )
#         elif self.request.GET.get('price'):
#             products = Product.objects.filter(query).order_by(price)
#         else:
#             products = Product.objects.filter(query)
#
#         return products
#
#
# class ProductSearchView(generic.ListView):
#     """Поиск товаров"""
#
#     paginate_by = 35
#     model = Product
#     context_object_name = 'products'
#
#     cart_product_form = CartAddProductForm()
#     search_form = ProductSearchForm()
#     filter_form = ProductFilterForm()
#
#     extra_context = {
#         'cart_product_form': cart_product_form,
#         'search_form': search_form,
#         'filter_form': filter_form,
#     }
#
#     def get_queryset(self):
#         query = Q(available=True) & (Q(status=2) | Q(status=3))
#         if self.request.GET.get('search_text'):
#             products = Product.objects.filter(query,
#                                               title__icontains=self.request.GET.get('search_text'))
#         else:
#             products = Product.objects.filter(query)
#
#         return products
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['search_text'] = f'search_text={self.request.GET.get("search_text")}&'
#         return context
#
#
# class ProductList(generic.ListView):
#
#     model = Product
#     context_object_name = 'products'
#     queryset = Product.objects.filter(Q(available=True) & (Q(status=2) | Q(status=3)))
#     paginate_by = 35
#
#     cart_product_form = CartAddProductForm()
#     search_form = ProductSearchForm()
#     filter_form = ProductFilterForm()
#
#     extra_context = {
#         'cart_product_form': cart_product_form,
#         'search_form': search_form,
#         'filter_form': filter_form,
#     }
#     template_name = 'products/product_list.html'
#
#
# def product_detail(request, slug):
#     product_id = Product.objects.get(slug=slug).id
#
#     cart = Cart(request)
#     quantity = cart.counter(str(product_id))
#     product = get_object_or_404(Product,
#                                 Q(id=product_id),
#                                 Q(slug=slug),
#                                 Q(available=True),
#                                 Q(status=2) | Q(status=3))
#
#     cart_product_form = CartAddProductForm()
#
#     context = {
#         'product': product,
#         'cart_bouquet_form': cart_product_form,
#         'quantity': quantity,
#     }
#     return render(request, template_name='products/product_detail.html', context=context)