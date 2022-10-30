from django.db import models

# import for get_absolute_url
from django.urls import reverse

from django.db.models import Case, Value, When


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория цветка'
        verbose_name_plural = 'Категории цветов'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_flower', kwargs={'slug': self.slug})


class Flower(models.Model):
    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.PROTECT
    )
    title = models.CharField(verbose_name='Название', max_length=100)
    slug = models.SlugField(verbose_name='Название на английском', unique=True)
    description = models.CharField(verbose_name='Описание', max_length=250)
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(verbose_name='Скидка в %', default=0)
    stock = models.PositiveIntegerField(verbose_name='Остаток на складе', default=0)
    available = models.BooleanField(verbose_name='Отображается в каталоге', default=False)
    only_on_order = models.BooleanField(verbose_name='Только под заказ', default=False)

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'
        unique_together = ('slug', )  # делает поле уникальным

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('flowers', kwargs={'slug': self.slug})


class GalleryFlower(models.Model):
    image = models.ImageField(upload_to='images')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name='img')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class Bouquet(models.Model):
    title = models.CharField(verbose_name='Название', max_length=150)
    slug = models.SlugField(verbose_name='Название на английском', unique=True)
    description = models.CharField(verbose_name='Описание', max_length=250)
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(verbose_name='Скидка в %', default=0)
    stock = models.PositiveIntegerField(verbose_name='Остаток на складе', default=0)
    available = models.BooleanField(verbose_name='Отображается в каталоге', default=False)
    only_on_order = models.BooleanField(verbose_name='Только под заказ', default=False)

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'
        unique_together = ('slug',)  # делает поле уникальным

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bouquets', kwargs={'slug': self.slug})

# class GalleryBouquet(models.Model):
#     image = models.ImageField(upload_to='images')
#     flower = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name='img')

# class CompositionOfTheBouquet(models.Model):
#     composition = models.ForeignKey(
#         Flower, verbose_name='Состав', on_delete=models.PROTECT
#     )
#     composition_bouquet = models.ForeignKey(
#         Flower, verbose_name='Состав', on_delete=models.PROTECT
#     )