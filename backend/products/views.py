from django.shortcuts import render
from .models import Category, Flower


from django.views.generic import ListView


class ListProduct(ListView):
    model = Flower
    template_name = 'products/index.html'

    # какие поля будут отправляться в шаблон
    fields = '__all__'
    # под каким названием будут лететь строчки из таблицы в шаблон
    context_object_name = 'flowers'


# def index(request):
#     category = Category.objects.all()
#     flower = Flower.objects.all()
#
#     return render(request, 'products/index.html', {
#         'categories': category,
#         'flowers': flower,
#     })