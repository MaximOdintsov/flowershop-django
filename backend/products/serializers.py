from rest_framework import serializers
from . import models


class GalleryFlowerSerializer(serializers.ModelSerializer):
    """ Галерея отдельно взятого цветка """

    class Meta:
        model = models.GalleryFlower
        fields = ('image', )


class FlowerListSerializer(serializers.Serializer):

    category_id = serializers.IntegerField()
    title = serializers.CharField()
    preview = serializers.ImageField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    discount_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    discount = serializers.IntegerField()
    status = serializers.IntegerField()



# class FlowerListSerializer(serializers.ModelSerializer):
#     """ Отображение в каталоге """
#     category = serializers.StringRelatedField(read_only=True)
#
#     class Meta:
#         model = models.Flower
#         fields = (
#             'id',
#             'preview',
#             'category',
#             'title',
#             'price',
#             'discount_price',
#             'discount',
#         )


class FlowerDetailSerializer(serializers.ModelSerializer):
    """ Отображение отдельно взятого цветка """

    category = serializers.StringRelatedField(read_only=True)
    # показывает поля CHOICES в текстовом формате
    status = serializers.CharField(read_only=True, source='get_status_display')
    flower_gallery = GalleryFlowerSerializer(read_only=True, many=True)

    class Meta:
        model = models.Flower
        exclude = (
            'slug',
            'new_arrival',
            'whole_stock',
            'stock_in_bouquets',
            'stock_for_sale',
            'available',
        )

