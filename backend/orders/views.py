from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import View, FormView, TemplateView

from .models import Order
from .forms import OrderCreateForm, AddQuantityForm
from products.models import Product

from products.forms import ProductSearchForm, ProductFilterForm


class AddItemToCart(LoginRequiredMixin, FormView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    form_class = AddQuantityForm
    template_name = 'products/product_list.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        quantity = form.cleaned_data['quantity']
        if quantity:
            cart = Order.get_cart(self.request.user)
            product = get_object_or_404(Product, pk=self.kwargs['pk'])
            try:
                item = cart.orderitem_set.get(product=product)
                item.quantity = quantity
                item.save(update_fields=['quantity'])
            except Exception:
                cart.orderitem_set.create(product=product,
                                          quantity=quantity)
        return super(AddItemToCart, self).form_valid(form)


class AddOneItemToCart(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, pk):
        cart = Order.get_cart(request.user)
        product = get_object_or_404(Product, pk=pk)

        try:
            item = cart.orderitem_set.get(product=product)
            item.quantity += 1
            item.save(update_fields=['quantity'])
        except Exception:
            cart.orderitem_set.create(product=product,
                                      quantity=1)

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class RemoveItemToCart(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, pk):
        cart = Order.get_cart(request.user)
        product = get_object_or_404(Product, pk=pk)

        try:
            item = cart.orderitem_set.get(product=product)
            item.delete()
        finally:
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class RemoveOneItemToCart(LoginRequiredMixin, View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, pk):
        cart = Order.get_cart(request.user)
        product = get_object_or_404(Product, pk=pk)

        try:
            item = cart.orderitem_set.get(product=product)
            if item.quantity > 1:
                item.quantity -= 1
                item.save(update_fields=['quantity'])
            elif item.quantity == 1:
                item.delete()
            else:
                raise ValidationError('Этот товар нельзя удалить')
        finally:
            return redirect('cart')


@login_required(login_url=reverse_lazy('login'))
def cart_view(request):
    cart = Order.get_cart(request.user)
    items = cart.orderitem_set.all()

    cart_add_quantity_form = AddQuantityForm()
    search_form = ProductSearchForm()
    filter_form = ProductFilterForm()

    context = {
        'cart': cart,
        'items': items,
        'cart_add_quantity_form': cart_add_quantity_form,
        'search_form': search_form,
        'filter_form': filter_form,
    }

    return render(request, 'orders/cart.html', context)


class OrderCreateView(LoginRequiredMixin, FormView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    form_class = OrderCreateForm
    template_name = 'orders/order_create.html'
    success_url = reverse_lazy('order_created')

    def get(self, request, *args, **kwargs):
        cart = Order.get_cart(self.request.user)
        items = cart.orderitem_set.all()
        if len(items):
            context = self.get_context_data(**kwargs)
            context['cart'] = cart
            context['items'] = items
            return self.render_to_response(context)
        else:
            return redirect('cart')

    def form_valid(self, form):
        cart = Order.get_cart(self.request.user)
        cart.make_order()
        data = form.cleaned_data

        cart.first_name = data['first_name']
        cart.phone = data['phone']
        cart.address = data['address']
        cart.receipt_method = data['receipt_method']
        cart.payment_method = data['payment_method']

        cart.save(update_fields=['first_name',
                                 'phone',
                                 'address',
                                 'receipt_method',
                                 'payment_method'])

        return super(OrderCreateView, self).form_valid(form)


class OrderCreatedView(TemplateView):
    template_name = 'orders/order_created.html'

# class OrderCreateView(LoginRequiredMixin, View):
#     login_url = '/login'
#     redirect_field_name = 'redirect_to'
#     template_name = 'orders/order_create.html'
#
#     def get(self, request):
#         cart = Order.get_cart(request.user)
#         items = cart.orderitem_set.all()
#         if len(items):
#             context = {
#                 'form': OrderCreateForm
#             }
#             return render(request, self.template_name, context)
#         else:
#             return redirect('cart')
#
#     def post(self, request):
#         form = OrderCreateForm(request.POST)
#         user = request.user
#
#         cart = Order.get_cart(request.user)
#         items = cart.orderitem_set.all()
#         if len(items):
#             if form.is_valid():
#                 cart = Order.get_cart(user)
#                 order = form.save(user=user.id)
#
#                 for item in cart:
#                     OrderItem.objects.create(order=order,
#                                              product=item['product'],
#                                              price=item['discount_price'],
#                                              quantity=item['quantity'])
#                 # очистка корзины
#                 cart.clear()
#                 return render(request, 'orders/order_created.html',
#                               context={'order': order})
#             else:
#                 return render(request, 'orders/order_create.html', context={'form': form})
#
#         else:
#             return redirect('cart')