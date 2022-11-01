from django.contrib import admin
from django.db.models import F

from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse


class GalleryFlowerInline(admin.TabularInline):
    model = GalleryFlower


class GalleryBouquetInline(admin.TabularInline):
    model = GalleryBouquet


class CompositionOfTheBouquetInline(admin.TabularInline):
    model = CompositionOfTheBouquet


@admin.register(Category)
class Category(admin.ModelAdmin):
    pass


@admin.register(Flower)
class Flower(admin.ModelAdmin):
    inlines = [GalleryFlowerInline, ]
    fields = ('category', 'title',  # 'slug',
              'description', ('price', 'discount'), 'whole_stock', ('available', 'only_on_order'))
    # filter_horizontal = ('category', )


@admin.register(Bouquet)
class Bouquet(admin.ModelAdmin):
    inlines = [GalleryBouquetInline, CompositionOfTheBouquetInline, ]  # можно несколько объектов в список
    fields = ('title', 'slug', 'description',
              ('price', 'discount'), 'stock', ('available', 'only_on_order'))
