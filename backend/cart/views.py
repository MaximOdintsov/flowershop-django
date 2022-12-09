from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import View

from products.models import Bouquet
from .cart import Cart
from .forms import CartAddBouquetForm


def cart_add_all(request, bouquet_id):
    cart = Cart(request)
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    form = CartAddBouquetForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(bouquet=bouquet,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('cart:cart_detail')


def cart_remove_all(request, bouquet_id):
    cart = Cart(request)
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    cart.remove(bouquet)
    return redirect('cart:cart_detail')


def cart_add_one(request, bouquet_id):
    cart = Cart(request)
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)

    cart.add_one(bouquet=bouquet,
                 quantity=1,
                 update_quantity=True)

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def cart_remove_one(request, bouquet_id):
    cart = Cart(request)
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)

    if cart.counter(str(bouquet_id)) >= 0:
        cart.add_one(bouquet=bouquet,
                     quantity=-1,
                     update_quantity=True)
    else:
        raise ValidationError('Это значение не должно быть отрицательным')
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


def cart_detail(request):
    cart = Cart(request)
    # quantity = self.cart[bouquet_id]['quantity']

    context = {
        'cart': cart
    }
    return render(request, 'cart/cart_detail.html', context=context)


