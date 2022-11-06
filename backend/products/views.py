from django.db.models import Sum, F
from django.shortcuts import render
from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet

from django.views.generic import ListView

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers


class FlowerListView(APIView):
    """ Вывод списка цветов """

    def get(self, request):
        flowers = Flower.objects.filter(available=True)
        serializer = serializers.FlowerListSerializer(flowers, many=True)
        return Response(serializer.data)


# показывает неверные ссылки
class FlowerDetailView(APIView):
    """ Вывод списка цветов """

    def get(self, request, pk):
        flower = Flower.objects.get(id=pk, available=True)
        serializer = serializers.FlowerDetailSerializer(flower)
        return Response(serializer.data)


class FlowerGalleryView(generics.ListAPIView):
    """ Показывает правильные ссылки """
    queryset = GalleryFlower.objects.all()
    serializer_class = serializers.GallerySerializer

#
# def index(request):
#
#     return render(request, 'products/index.html')
#
#
# def flower(request):
#     flowers = Flower.objects.all()
#     gallery = GalleryFlower.objects.all()
#
#     # сделать вычисления (stock_for_sale = whole_stock - stock_in_bouquets)
#
#     return render(request, 'products/flowers.html', {
#         'flowers': flowers,
#
#         # 'gallery': gallery,
#         'gallery': Flower.objects.all()[3].flower_gallery.all(),
#
#         # 'gallery':  Flower.objects.get(id=10).flower_gallery.all()[0].image,
#     })
#
#
# def bouquet(request):
#     bouquets = Bouquet.objects.all()
#     gallery = GalleryBouquet.objects.all()
#     compositions = CompositionOfTheBouquet.objects.all()
#
#     # сделать вычисления (stock_for_sale = whole_stock - stock_in_bouquets)
#
#     return render(request, 'products/bouquets.html', {
#         'bouquets': bouquets,
#         'gallery': gallery,
#         'compositions': compositions,
#     })