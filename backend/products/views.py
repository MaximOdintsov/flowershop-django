from django.db.models import Q
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
        search_form = ProductSearchForm()
        filter_form = ProductFilterForm()

        context = super().get_context_data(**kwargs)
        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        finally:
            context['cart_add_quantity_form'] = cart_add_quantity_form
            context['search_form'] = search_form
            context['filter_form'] = filter_form

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
    paginate_by = 30
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
        search_form = ProductSearchForm()
        filter_form = ProductFilterForm()

        context = super().get_context_data(**kwargs)
        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        finally:
            context['cart_add_quantity_form'] = cart_add_quantity_form
            context['search_form'] = search_form
            context['filter_form'] = filter_form

            return context


class ProductList(generic.ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(Q(status=2) | Q(status=3))
    paginate_by = 30
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        cart_add_quantity_form = AddQuantityForm()
        search_form = ProductSearchForm()
        filter_form = ProductFilterForm()

        context = super().get_context_data(**kwargs)
        try:
            cart = Order.get_cart(self.request.user)
            items = cart.orderitem_set.all()
            context['cart'] = cart
            context['items'] = items
        finally:
            context['cart_add_quantity_form'] = cart_add_quantity_form
            context['search_form'] = search_form
            context['filter_form'] = filter_form

            return context

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