from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.urls import reverse_lazy
from backend import settings

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import View, FormView

from .models import Order
from .forms import OrderCreateForm, AddQuantityForm
from products.models import Product

from products.forms import ProductSearchForm, ProductFilterForm


class AddItemToCart(LoginRequiredMixin, FormView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    form_class = AddQuantityForm
    template_name = 'products/product_list.html'
    success_url = reverse_lazy('cart')

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
    items = cart.orderitem_set.order_by('creation_time')

    cart_add_quantity_form = AddQuantityForm()
    filter_form = ProductFilterForm()

    available = 1
    for item in items:
        if item.product.status == 1 or item.product.status == 4:
            available = 0

    context = {
        'cart': cart,
        'items': items,
        'cart_add_quantity_form': cart_add_quantity_form,
        'filter_form': filter_form,
        'available': available,
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
        available = 1
        for item in items:
            if item.product.status == 1 or item.product.status == 4:
                available = 0
                return redirect('cart')

        if len(items):
            context = self.get_context_data(**kwargs)
            context['cart'] = cart
            context['items'] = items
            context['available'] = available
            return self.render_to_response(context)
        else:
            return redirect('cart')

    def form_valid(self, form):
        cart = Order.get_cart(self.request.user)
        cart.make_order()
        cart.make_order_on_site()
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

        message = f'Сумма заказа:{cart.amount} руб.\n' \
                  f'Имя: {cart.first_name}\nНомер телефона: {cart.phone}\n' \
                  f'Адрес: {cart.address}\nСпособ получения: {cart.receipt_method}\n' \
                  f'Заказы на сайте: https://kirovcvetok.ru/admin/orders/order/'
        send_mail(
            f'Новый заказ №{cart.id} от {cart.creation_time}',
            message,
            settings.EMAIL_HOST_USER,
            ['olga.odintsova@kirovcvetok.ru'],
            fail_silently=False,
        )
        return super(OrderCreateView, self).form_valid(form)
