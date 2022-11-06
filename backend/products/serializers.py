from rest_framework import serializers
from . import models as model


class FlowerListSerializer(serializers.ModelSerializer):
    """ Отображение в каталоге """

    class Meta:
        model = model.Flower
        fields = (
            'category',
            'title',
            'price',
            'discount_price',
            'discount',
        )


class GalleryFlowerSerializer(serializers.ModelSerializer):
    """ Галерея отдельно взятого цветка """

    class Meta:
        model = model.GalleryFlower
        fields = ('image', )


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = model.GalleryFlower
        fields = ('image', )


class FlowerDetailSerializer(serializers.ModelSerializer):
    """ Отображение в каталоге """

    flower_gallery = GalleryFlowerSerializer(many=True)

    class Meta:
        model = model.Flower
        exclude = (
            'slug',
            'new_arrival',
            'whole_stock',
            'stock_in_bouquets',
            'stock_for_sale',
            'available',
        )