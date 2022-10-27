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
    title = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=200)
    # color =
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    image = models.ImageField(verbose_name='Изображение', upload_to="flowers")
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(
        Case(
            When(stock=0, then=False),
            default=True
        )
    )

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('flowers', kwargs={'slug': self.slug})

