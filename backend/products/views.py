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


def index(request):
    category = Category.objects.all()
    flowers = Flower.objects.all()
    bouquets = Bouquet.objects.all()
    compositions = CompositionOfTheBouquet.objects.all()

    # считает сумму цветов, которые задействованы в букетах
    for composition in compositions:
        flower = Flower.objects.get(id=composition.flower.id)
        flower.stock_in_bouquets = composition.bouquet.stock * composition.count
        flower.save()

    for flower in flowers:
        flower.save()

    return render(request, 'products/index.html', {
        'categories': category,
        'flowers': flowers,
        'compositions': compositions,
    })