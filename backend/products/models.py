from django.db import models

# import for get_absolute_url
from django.urls import reverse

from django.db.models import Case, Value, When, F, Sum
from django.utils.text import slugify


class Category(models.Model):
    """ Класс добавления категории цветов """
    title = models.CharField(max_length=100, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория цветка'
        verbose_name_plural = 'Категории цветов'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_flower', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """ Переводит поле title с ru на en и сохраняет в slug """
        # for translate slug
        from translate import Translator
        translator = Translator(from_lang='ru', to_lang='en')
        translated_title = translator.translate(self.title)
        self.slug = slugify(translated_title)
        super(Category, self).save(*args, **kwargs)


class Flower(models.Model):
    """ Класс добавления цветка """
    SALE = 1
    ORDER = 2
    UNAVAILABLE = 3

    STATUS_CHOICES = [
        (UNAVAILABLE, 'Недоступно для продажи'),
        (ORDER, 'Только под заказ'),
        (SALE, 'Доступно для продажи'),
    ]

    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.PROTECT
    )
    title = models.CharField(verbose_name='Название', max_length=100)
    slug = models.SlugField(verbose_name='Название на английском', max_length=150, unique=True, null=True, default='')
    description = models.CharField(verbose_name='Описание', max_length=250)
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(verbose_name='Скидка в %', default=0)

    whole_stock = models.PositiveIntegerField(verbose_name='Весь запас', default=0)
    stock_in_bouquets = models.PositiveIntegerField(verbose_name='Цветы в букетах', default=0)
    stock_for_sale = models.PositiveIntegerField(verbose_name='Остаток для продажи', default=0)

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=UNAVAILABLE,
        verbose_name='Статус',
    )

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'
        unique_together = ('slug', )  # делает поле уникальным

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('flowers', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """ Переводит поле title с ru на en и сохраняет в slug """
        # for translate slug
        from translate import Translator
        translator = Translator(from_lang='ru', to_lang='en')
        translated_title = translator.translate(self.title)
        self.slug = slugify(translated_title)
        super(Flower, self).save(*args, **kwargs)


class GalleryFlower(models.Model):
    """ Класс добавления картинок в цветок """
    image = models.ImageField(upload_to='images')
    flower_gallery = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name='flower_gallery')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class Bouquet(models.Model):
    """ Класс создания букета """
    SALE = 1
    ORDER = 2
    UNAVAILABLE = 3

    STATUS_CHOICES = [
        (UNAVAILABLE, 'Недоступно для продажи'),
        (ORDER, 'Только под заказ'),
        (SALE, 'Доступно для продажи'),
    ]

    title = models.CharField(verbose_name='Название', max_length=150)
    slug = models.SlugField(verbose_name='Название на английском', max_length=150, unique=True)
    description = models.CharField(verbose_name='Описание', max_length=250)
    price = models.DecimalField(verbose_name='Цена', max_digits=7, decimal_places=2)
    discount = models.PositiveIntegerField(verbose_name='Скидка в %', default=0)
    stock = models.PositiveIntegerField(verbose_name='Количество букетов', default=0)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=UNAVAILABLE,
        verbose_name='Статус',
    )

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'
        unique_together = ('slug',)  # делает поле уникальным

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bouquets', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """ Переводит поле title с ru на en и сохраняет в slug """
        # for translate slug
        from translate import Translator
        translator = Translator(from_lang='ru', to_lang='en')
        translated_title = translator.translate(self.title)
        self.slug = slugify(translated_title)
        super(Bouquet, self).save(*args, **kwargs)


class GalleryBouquet(models.Model):
    """ Класс добавления картинок в букет """
    image = models.ImageField(upload_to='images')
    bouquet_gallery = models.ForeignKey(Bouquet, on_delete=models.CASCADE, related_name='bouquet_gallery')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class CompositionOfTheBouquet(models.Model):
    """ Класс сохранения цветов в букете """
    # для связи между букетом и композицией
    bouquet_composition = models.ForeignKey(
        Bouquet, verbose_name='Букет', on_delete=models.PROTECT, related_name='bouquet_composition'
    )
    # для выбора цветка в букет
    flower = models.ForeignKey(
        Flower, verbose_name='Выбрать цветок', on_delete=models.PROTECT, db_column='flower'
    )
    # количество цветка в букете
    count = models.PositiveIntegerField(verbose_name='Количество цветов', default=0)
    # общее количество цветов в букетах (количество букетов * количество цветка в букете)
    total_count = models.PositiveIntegerField(
        verbose_name='Общее количество цветов в этом букете',
        default=0
    )

    def __str__(self):
        return f'{self.flower.title}'

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'

    def delete(self, *args, **kwargs):
        flowers = Flower.objects.get(id=self.flower.id)
        # удаляем значение из общего количества цветов в букетах
        flowers.stock_in_bouquets -= self.total_count
        flowers.save()
        super(CompositionOfTheBouquet, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        flowers = Flower.objects.get(id=self.flower.id)
        # удаляем старое значение из общего количества цветов в букетах
        flowers.stock_in_bouquets -= self.total_count
        # присваиваем новое значение
        self.total_count = self.bouquet_composition.stock * self.count

        flowers.stock_in_bouquets += self.total_count
        flowers.save()
        super(CompositionOfTheBouquet, self).save(*args, **kwargs)



