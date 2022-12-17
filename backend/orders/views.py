from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


def order_create(request):
    cart = Cart(request)

    form = OrderCreateForm(request.POST)

    if form.is_valid():
        user = request.user
        if user.is_authenticated:
            order = form.save(user.id)
        else:
            order = form.save()

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
        form = form
    return render(request, 'orders/create.html', context={'form': form})