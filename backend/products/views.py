from django.db.models import Sum, F
from django.shortcuts import render
from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet

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
#     context_object_name = 'flower_images


def index(request):

    return render(request, 'products/index.html')


def flower(request):
    flowers = Flower.objects.all()
    gallery = GalleryFlower.objects.all()

    # сделать вычисления (stock_for_sale = whole_stock - stock_in_bouquets)

    return render(request, 'products/flowers.html', {
        'flowers': flowers,

        # 'gallery': gallery,
        'gallery': Flower.objects.all()[3].flower_gallery.all(),

        # 'gallery':  Flower.objects.get(id=10).flower_gallery.all()[0].image,
    })


def bouquet(request):
    bouquets = Bouquet.objects.all()
    gallery = GalleryBouquet.objects.all()
    compositions = CompositionOfTheBouquet.objects.all()

    # сделать вычисления (stock_for_sale = whole_stock - stock_in_bouquets)

    return render(request, 'products/bouquets.html', {
        'bouquets': bouquets,
        'gallery': gallery,
        'compositions': compositions,
    })