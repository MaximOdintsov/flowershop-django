from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import (Product)

from cart.forms import CartAddProductForm
from cart.cart import Cart


def contacts(request):
    return render(request, template_name='products/contacts.html')


def home(request):

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    return render(
        request, 
        template_name='products/index.html',
        context={
            'num_visits': num_visits,
        }
    )


class ProductList(generic.ListView):

    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(Q(available=True) & (Q(status=2) | Q(status=3)))
    paginate_by = 10

    cart_product_form = CartAddProductForm()
    extra_context = {
        'cart_product_form': cart_product_form,
    }
    template_name = 'products/product_list.html'


def product_detail(request, slug):
    product_id = Product.objects.get(slug=slug).id

    cart = Cart(request)
    quantity = cart.counter(str(product_id))
    product = get_object_or_404(Product,
                                Q(id=product_id),
                                Q(slug=slug),
                                Q(available=True),
                                Q(status=2) | Q(status=3))

    cart_product_form = CartAddProductForm()

    context = {
        'product': product,
        'cart_bouquet_form': cart_product_form,
        'quantity': quantity,
    }
    return render(request, template_name='products/product_detail.html', context=context)

