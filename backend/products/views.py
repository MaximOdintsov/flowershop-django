from django.db.models import Sum, F
from django.shortcuts import render
from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet

from django.views.generic import ListView

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

from . import serializers

from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer


# class FlowerListView(APIView):
#     """ Вывод списка цветов """
#
#     def get(self, request):
#         flowers = Flower.objects.filter(available=True)
#         serializer = serializers.FlowerListSerializer(flowers, many=True)
#         return Response(serializer.data)

class FlowerListView(APIView):
    """ Вывод списка цветов """

    def get(self, request):
        flowers = Flower.objects.filter(available=True)
        serializer = serializers.FlowerListSerializer(flowers, many=True).data
        return Response({'posts': serializer})

    # def post(self, request):
    #     post_new = Flower.objects.create(
    #         category=request.data['category']
    #     )

# показывает неверные ссылки на картинки
class FlowerDetailView(APIView):
    """ Вывод списка цветов """

    def get(self, request, pk):
        flower = Flower.objects.get(id=pk, available=True)
        serializer = serializers.FlowerDetailSerializer(flower)
        return Response(serializer.data)


# class FlowerGalleryView(generics.ListAPIView):
#     """ Показывает правильные ссылки """
#
#     queryset = GalleryFlower.objects.all()
#     serializer_class = serializers.GalleryFlowerSerializer


# class FlowerGalleryView(APIView):
#     """ Вывод списка цветов """
#
#     def get(self, request, pk):
#         queryset = GalleryFlower.objects.filter(flower_gallery_id=pk).values()
#         serializer = serializers.GalleryFlowerSerializer
#
#         return Response({'model_to_return': queryset})


# class FlowerGalleryView(APIView):
#     """ Вывод списка цветов """
#     # только строки
#     def get(self, request):
#         queryset = GalleryFlower.objects.all()
#         context = {'request': request}
#         serializer = serializers.GalleryFlowerSerializer(context=context)
#         return Response(queryset, serializer.data)

class FlowerGalleryView(APIView):
    """ Вывод списка цветов """

    renderer_classes = [JSONRenderer]

    def get(self, request, pk):
        queryset = GalleryFlower.objects.filter(flower_gallery_id=pk).count()
        content = {'flower_gallery_image': queryset}
        # serializer = serializers.GalleryFlowerSerializer

        return Response({'model_to_return': queryset})

