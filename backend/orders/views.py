from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from cart.cart import Cart
from django.urls import reverse_lazy
from django.views.generic import View

from .models import Order, OrderItem
from .forms import OrderCreateForm, AddQuantityForm
from products.models import Product


@login_required(login_url=reverse_lazy('login'))
def add_item_to_cart(request, pk):
    if request.method == 'POST':
        quantity_form = AddQuantityForm(request.POST)
        if quantity_form.is_valid():
            quantity = quantity_form.cleaned_data['quantity']
            if quantity:
                cart = Order.get_cart(request.user)
                # product = Product.objects.get(pk=pk)
                product = get_object_or_404(Product, pk=pk, )
                cart.orderitem_set.create(product=product,
                                          quantity=quantity,
                                          price=product.price)
                cart.save()
                return redirect('cart_view')
        else:
            pass
    return redirect('shop')


class OrderCreateView(View):
    template_name = 'orders/create.html'

    def get(self, request):
        context = {
            'form': OrderCreateForm
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = OrderCreateForm(request.POST)
        user = request.user

        if user.is_authenticated:
            if form.is_valid():
                cart = Order.get_cart(user)
                order = form.save(user=user.id)

                for item in cart:
                    OrderItem.objects.create(order=order,
                                             product=item['product'],
                                             price=item['discount_price'],
                                             quantity=item['quantity'])
                # очистка корзины
                cart.clear()
                return render(request, 'orders/created.html',
                              context={'order': order})
            else:
                return render(request, 'orders/create.html', context={'form': form})
        else:
            return redirect('login')
