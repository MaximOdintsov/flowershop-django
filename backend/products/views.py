from django.db.models import Q
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.views import generic


from .models import Product
from .forms import ProductSearchForm, ProductFilterForm

# from cart.forms import CartAddProductForm
# from cart.cart import Cart

from orders.models import Order, OrderItem
from orders.forms import AddQuantityForm


class ProductFilterView(generic.ListView):
    """Фильтрация товаров"""
    model = Product
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        cart_add_quantity_form = AddQuantityForm()
        filter_form = ProductFilterForm()

        context = super().get_context_data(**kwargs)
        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        except Exception:
            pass
        finally:
            context['filter_form'] = filter_form
            context['cart_add_quantity_form'] = cart_add_quantity_form
        return context

    def get_queryset(self):

        if self.request.GET.get('price') == 'A':
            price = 'new_price'
        elif self.request.GET.get('price') == 'D':
            price = '-new_price'

        query = (Q(status=2) | Q(status=3))

        if self.request.GET.get('category'):
            if self.request.GET.get('price'):
                products = Product.objects.filter(
                    query,
                    category__in=self.request.GET.get('category'),
                ).order_by(price)
            else:
                products = Product.objects.filter(
                    query,
                    category__in=self.request.GET.get('category')
                )
        elif self.request.GET.get('price'):
            products = Product.objects.filter(query).order_by(price)
        else:
            products = Product.objects.filter(query)

        return products


class ProductSearchView(generic.ListView):
    """Поиск товаров"""
    paginate_by = 20
    model = Product
    context_object_name = 'products'

    def get_queryset(self):
        query = (Q(status=2) | Q(status=3))
        if self.request.GET.get('search_text'):
            products = Product.objects.filter(query,
                                              title__icontains=self.request.GET.get('search_text'))
        else:
            products = Product.objects.filter(query)

        return products

    def get_context_data(self, *args, **kwargs):
        cart_add_quantity_form = AddQuantityForm()
        filter_form = ProductFilterForm()

        context = super().get_context_data(**kwargs)
        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        except Exception:
            pass
        finally:
            context['filter_form'] = filter_form
            context['cart_add_quantity_form'] = cart_add_quantity_form
        return context


class ProductList(generic.ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(Q(status=2) | Q(status=3))
    paginate_by = 20
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        cart_add_quantity_form = AddQuantityForm()
        filter_form = ProductFilterForm()

        context = super().get_context_data(**kwargs)
        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        except Exception:
            pass
        finally:
            context['filter_form'] = filter_form
            context['cart_add_quantity_form'] = cart_add_quantity_form
        return context


class ProductDetailView(generic.DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/product_detail.html'

    def get_context_data(self, **kwargs):
        cart_add_quantity_form = AddQuantityForm()
        context = super().get_context_data(**kwargs)

        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        except Exception:
            pass
        finally:
            context['cart_add_quantity_form'] = cart_add_quantity_form
        return context