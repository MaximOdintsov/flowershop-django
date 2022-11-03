from django.db.models import Sum, F
from django.shortcuts import render
from .models import Category, Flower, Bouquet
from .models import GalleryFlower, CompositionOfTheBouquet

from django.views.generic import ListView


# class ListFlower(ListView):
#     model = Flower
#     template_name = 'products/index.html'
#
#     # какие поля будут отправляться в шаблон
#     fields = '__all__'
#     # под каким названием будут лететь строчки из таблицы в шаблон
#     context_object_name = 'flowers'
#
#     flowers = Flower.objects.all()
#     for flower in flowers:
#         flower.save()

    # add math
    # def substract(request):
    #     flower = Flower.objects.all()
    #     composition = CompositionOfTheBouquet.objects.all()
    #     foo = flower.stock - composition.count
    #     return foo


# class ListFlowerImages(ListView):
#     model = GalleryFlower
#     template_name = 'products/index.html'
#
#     # какие поля будут отправляться в шаблон
#     fields = '__all__'
#     # под каким названием будут лететь строчки из таблицы в шаблон
#     context_object_name = 'flower_images'
async def save_composition():
    compositions = CompositionOfTheBouquet.objects.all()
    async for composition in compositions:
        await composition.save()


def index(request):
    bouquets = Bouquet.objects.all()
    compositions = CompositionOfTheBouquet.objects.all()

    save_composition()

    # сделать вычисления (stock_for_sale = whole_stock - stock_in_bouquets)

    return render(request, 'products/index.html', {
        'bouquets': bouquets,
        'compositions': compositions,
    })
