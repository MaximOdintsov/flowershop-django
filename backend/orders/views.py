from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.views.generic import View


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
                cart = Cart(request)
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

# def order_create(request):
#     cart = Cart(request)
#
#     form = OrderCreateForm(request.POST)
#
#     if form.is_valid():
#         user = request.user
#         if user.is_authenticated:
#             order = form.save(user.id)
#         else:
#             order = form.save()
#
#         for item in cart:
#             OrderItem.objects.create(order=order,
#                                      product=item['product'],
#                                      price=item['discount_price'],
#                                      quantity=item['quantity'])
#         # очистка корзины
#         cart.clear()
#         return render(request, 'orders/created.html',
#                       context={'order': order})
#     else:
#         return render(request, 'orders/create.html', context={'form': form})