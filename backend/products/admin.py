from django.contrib import admin

from .models import Category, Flower


@admin.register(Category)
class Category(admin.ModelAdmin):
    pass


@admin.register(Flower)
class Flower(admin.ModelAdmin):
    pass
