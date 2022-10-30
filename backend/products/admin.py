from django.contrib import admin

from .models import Category, Flower, Bouquet
from .models import GalleryFlower


class GalleryFlowerInline(admin.TabularInline):
    model = GalleryFlower


# class GalleryBouquetInline(admin.TabularInline):
#     model = GalleryBouquet


# class CompositionOfTheBouquetInline(admin.TabularInline):
#     name = 'composition'
#     model = CompositionOfTheBouquet


@admin.register(Category)
class Category(admin.ModelAdmin):
    pass


@admin.register(Flower)  # в скобках прописать inline!
class Flower(admin.ModelAdmin):
    # inline_compositions = [CompositionOfTheBouquetInline, ]
    inlines = [GalleryFlowerInline, ]


@admin.register(Bouquet)
class Bouquet(admin.ModelAdmin):
    # inline_compositions1 = [CompositionOfTheBouquetInline, ]
    # inline_images1 = [GalleryBouquetInline, ]
    pass