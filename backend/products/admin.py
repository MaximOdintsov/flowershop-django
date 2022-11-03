from django.contrib import admin
from django.db.models import F

from .models import Category, Flower, Bouquet
from .models import GalleryFlower, GalleryBouquet, CompositionOfTheBouquet

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse


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
    fields = ('flower', 'count',)
    actions = ['save_composition', ]


@admin.register(Category)
class Category(admin.ModelAdmin):
    fields = ('title', )


@admin.register(Flower)
class Flower(admin.ModelAdmin):
    inlines = [GalleryFlowerInline, ]
    fields = ('category', 'title',  # 'slug',
              'description', ('price', 'discount'), 'whole_stock', 'status')


@admin.register(Bouquet)
class Bouquet(admin.ModelAdmin):
    inlines = [GalleryBouquetInline, CompositionOfTheBouquetInline, ]
    fields = ('title', 'description',
              ('price', 'discount'), 'stock', 'status')
    list_display = ['title', 'description', 'price', 'discount', 'stock', 'status']
    list_editable = ['price', 'discount', 'stock', 'status']
    list_per_page = 20  # сколько строк отображается на 1 странице
    ordering = ['status', ]  # сортировка

    actions = ['save_composition', ]

    @admin.action(description='Обновить значения')
    def save_composition(self, request, queryset):
        # обновляем Flower.stock_in_bouquets и рассчитываем Flower.stock_for_sale
        bouquets = queryset
        for bouquet in bouquets:
            flower_len = len(CompositionOfTheBouquet.objects.filter(bouquet_composition=bouquet))
            flowers = CompositionOfTheBouquet.objects.filter(bouquet_composition=bouquet)
            for flower in flowers:
                # сохраняем поле CompositionOfTheBouquet
                save_composition = CompositionOfTheBouquet.objects.get(id=flower.id)
                save_composition.save()

        # рассчитать Flower.stock_for_sale
        self.message_user(
            request,
            f'Было обновлено {len(bouquets)} записей'
        )
