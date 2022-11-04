from django.contrib import admin
from django.db import models

from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet

from django.contrib import admin

from django.forms import TextInput, IntegerField


class GalleryFlowerInline(admin.TabularInline):
    model = GalleryFlower
    # fk_name = 'flower_gallery'
    extra = 0


class GalleryBouquetInline(admin.TabularInline):
    model = GalleryBouquet
    # fk_name = 'bouquet_gallery'
    extra = 0


class CompositionOfTheBouquetInline(admin.StackedInline):
    model = CompositionOfTheBouquet
    # fk_name = 'bouquet_composition'
    extra = 0
    fields = ('flower', 'count', )
    actions = ['save_composition', ]


@admin.register(Category)
class Category(admin.ModelAdmin):
    fields = ('title', )


@admin.register(Flower)
class Flower(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {
            'widget': TextInput(attrs={'size': 10})
        },
    }

    inlines = [GalleryFlowerInline, ]
    fields = ('category', 'title',  # 'slug',
              'description', ('price', 'discount'), 'whole_stock', 'status')
    list_display = ['title', 'price', 'discount', 'discount_price', 'new_arrival', 'whole_stock', 'stock_for_sale', 'status', ]
    list_editable = ['price', 'discount', 'new_arrival', 'status', ]
    list_per_page = 20  # сколько строк отображается на 1 странице
    ordering = ['status', ]  # сортировка


@admin.register(Bouquet)
class Bouquet(admin.ModelAdmin):
    formfield_overrides = {
        models.DecimalField: {
            'widget': TextInput(attrs={'size': 10})
        },
    }

    inlines = [GalleryBouquetInline, CompositionOfTheBouquetInline, ]
    fields = ('title', 'description',
              ('price', 'discount'), 'stock', 'status')
    list_display = ['title', 'price', 'discount', 'discount_price', 'stock', 'status']
    list_editable = ['price', 'discount', 'stock', 'status']
    list_per_page = 20  # сколько строк отображается на 1 странице
    ordering = ['status', ]  # сортировка

    actions = ['save_composition', ]

    @admin.action(description='Обновить значения')
    def save_composition(self, request, queryset):
        # обновляем Flower.stock_in_bouquets и рассчитываем Flower.stock_for_sale
        bouquets = queryset
        for bouquet in bouquets:
            bouquet = bouquet
            bouquet.save()

        self.message_user(
            request,
            f'Было обновлено {len(bouquets)} записей'
        )
