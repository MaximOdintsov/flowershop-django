from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views import generic

from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet


from . import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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


class FlowerList(generic.ListView):

    model = Flower
    context_object_name = 'flowers'
    queryset = Flower.objects.filter(available=True)
    paginate_by = 20
    template_name = 'flower_list.html'

def flower_detail(request, slug):
    id_flower = Flower.objects.get(slug=slug).id

    flower = get_object_or_404(Flower, slug=slug)
    gallery_flower = GalleryFlower.objects.filter(flower_gallery_id=id_flower)
    context = {
        'flower': flower,
        'gallery_flower': gallery_flower,
    }
    return render(request, template_name='products/flower_detail.html', context=context)


def bouquet_list(request):
    bouquets = get_list_or_404(Bouquet, available=True)

    context = {
        'bouquets': bouquets,
    }
    return render(request, template_name='products/bouquet_list.html', context=context)


def bouquet_detail(request, slug):
    id_bouquet = Bouquet.objects.get(slug=slug).id

    bouquet = get_object_or_404(Bouquet, slug=slug)
    gallery_bouquet = GalleryBouquet.objects.filter(bouquet_gallery_id=id_bouquet)
    composition = CompositionOfTheBouquet.objects.filter(bouquet_composition_id=id_bouquet)
    context = {
        'bouquet': bouquet,
        'gallery_bouquet': gallery_bouquet,
        'composition': composition,
    }
    return render(request, template_name='products/bouquet_detail.html', context=context)


class FlowerListView(APIView):
    """ Вывод списка цветов """

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        flowers = Flower.objects.filter(available=True)
        serializer = serializers.FlowerListSerializer(flowers, many=True).data
        return Response({'posts': serializer})


class FlowerDetailView(APIView):
    """ Вывод отдельно взятого цветка """

    def get(self, request, pk):
        flower = Flower.objects.get(id=pk, available=True)
        serializer = serializers.FlowerDetailSerializer(flower)
        return Response(serializer.data)


class FlowerGalleryView(APIView):
    """ Вывод списка цветов """

    renderer_classes = [JSONRenderer]

    def get(self, request, pk):
        queryset = GalleryFlower.objects.filter(flower_gallery_id=pk).count()
        content = {'flower_gallery_image': queryset}
        # serializer = serializers.GalleryFlowerSerializer

        return Response({'model_to_return': queryset})


# class FlowerGalleryView(generics.ListAPIView):
#     """ Показывает правильные ссылки """
#
#     queryset = GalleryFlower.objects.all()
#     serializer_class = serializers.GalleryFlowerSerializer

