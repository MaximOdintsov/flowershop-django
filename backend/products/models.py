from django.db import models

# import for get_absolute_url
from django.urls import reverse

from django.db.models import Case, Value, When, F, Sum
from django.utils.text import slugify


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
    slug = models.SlugField(verbose_name='Название на английском', unique=True, null=True, default='')
    description = models.CharField(verbose_name='Описание', max_length=250)
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(verbose_name='Скидка в %', default=0)

    whole_stock = models.PositiveIntegerField(verbose_name='Весь запас', default=0)
    stock_in_bouquets = models.PositiveIntegerField(verbose_name='Цветы в букетах', default=0)
    all_stock = models.PositiveIntegerField(verbose_name='Остаток для продажи', default=0)

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

    # def save(self, *args, **kwargs):
    #     # for translate slug
    #     from translate import Translator
    #     translator = Translator(from_lang='ru', to_lang='en')
    #     translated_title = translator.translate(self.title)
    #     self.slug = slugify(translated_title)
    #     super(Flower, self).save(*args, **kwargs)


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
        return f'title = {self.title}'

    def get_absolute_url(self):
        return reverse('bouquets', kwargs={'slug': self.slug})


class GalleryBouquet(models.Model):
    image = models.ImageField(upload_to='images')
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE, related_name='img')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class CompositionOfTheBouquet(models.Model):
    flower = models.ForeignKey(
        Flower, verbose_name='Выбрать цветок', on_delete=models.PROTECT
    )
    bouquet = models.ForeignKey(
        Bouquet, verbose_name='Состав', on_delete=models.PROTECT
    )
    count = models.PositiveIntegerField(verbose_name='Количество', default=0)

    def __str__(self):
        return f'Flower = {self.flower}, Bouquet = {self.bouquet}, Count = {self.count}'

    # def save(self, *args, **kwargs):
    #     Flower.objects.all().stock_in_bouquets = 2+2
    #     super(CompositionOfTheBouquet, Flower, self).save(*args, **kwargs)

    # Flower.objects.annotate(
    #     count=Sum('CompositionOfTheBouquet_set__count'),
    #     bouquet=Sum('Bouquet_set__stock'),
    # ).annotate(
    #     stock_in_bouquets=F('count') + F('bouquet')
    # )

    # def save(self, *args, **kwargs):
    #     # flower = Flower.stock
    #     # bouquet = Bouquet.stock
    #     Flower.stock = int(self.flower.stock) - (int(self.bouquet.stock) * int(self.count))
    #     super(CompositionOfTheBouquet, self).save(*args, **kwargs)

    # @property
    # def counter(self):
    #     if self.count:
    #         # self.flower.stock = self.flower.stock - (self.count * self.bouquet.stock)
    #         # self.flower.stock.save()
    #         Flower.stock = int(Flower.stock) - (int(self.count) * int(Bouquet.stock))
    #         Flower.stock.save()
    #         print(Flower.stock)
    #         return Flower.stock

    # @property
    # def math(self):
    #     if self.count:
    #         x = self.count - self.flower.stock
    #         return x
    #     else:
    #         return '-'

