from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction

# import for get_absolute_url
from django.urls import reverse

from django.db.models import Case, Value, When, F, Sum
from django.utils.text import slugify


class Category(models.Model):
    """ Класс добавления категории цветов """

    title = models.CharField(max_length=100, verbose_name='Имя категории')
    slug = models.SlugField(verbose_name='Название на английском', max_length=150, unique=True, null=True, default=None)

    class Meta:
        verbose_name = 'Категория цветка'
        verbose_name_plural = 'Категории цветов'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_flower', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """ Переводит поле title с ru на en и сохраняет в slug """

        # сохраняем для определения id
        super(Category, self).save()

        # for translate slug
        if self.slug is None:
            import translators as ts
            translated_title = ts.google(self.title)
            self.slug = slugify(f'category{translated_title}{self.id}')

        super(Category, self).save(*args, **kwargs)


class Flower(models.Model):
    """ Класс добавления цветка """

    UNCHECKED = 1
    SALE = 2
    ORDER = 3
    UNAVAILABLE = 4

    STATUS_CHOICES = [
        (UNCHECKED, 'Находится на проверке'),
        (SALE, 'Доступно для продажи'),
        (ORDER, 'Только под заказ'),
        (UNAVAILABLE, 'Недоступно для продажи'),
    ]

    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.PROTECT
    )
    title = models.CharField(verbose_name='Название', max_length=100)
    slug = models.SlugField(verbose_name='Название на английском', max_length=150, unique=True, null=True, default=None)
    description = models.CharField(verbose_name='Описание', max_length=250)

    price = models.DecimalField(verbose_name='Цена без скидки', max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(verbose_name='Цена со скидкой', max_digits=8, decimal_places=2, default=0.00)
    discount = models.PositiveSmallIntegerField(
        verbose_name='Скидка в %',
        validators=[MinValueValidator(0), MaxValueValidator(80)]
    )

    new_arrival = models.PositiveSmallIntegerField(verbose_name='Новое поступление', default=0)
    whole_stock = models.PositiveSmallIntegerField(verbose_name='Весь запас', default=0)
    stock_in_bouquets = models.PositiveSmallIntegerField(verbose_name='Цветы в букетах', default=0)
    stock_for_sale = models.PositiveSmallIntegerField(verbose_name='Остаток для продажи', default=0)

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=UNCHECKED,
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

        # сохраняем для определения id
        super(Flower, self).save()

        # for translate slug
        if self.slug is None:
            import translators as ts
            translated_title = ts.google(self.title)
            self.slug = slugify(f'flower {translated_title} {self.id}')

        # прибавляем поступление цветов
        self.whole_stock += self.new_arrival
        # обнуляем поступление цветов
        self.new_arrival = 0

        # обновляем значение цветов, доступных для продажи
        self.stock_for_sale = self.whole_stock - self.stock_in_bouquets

        # рассчитываем цену со скидкой
        sale = (self.price/100) * self.discount
        self.discount_price = self.price - sale

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
    UNCHECKED = 1
    SALE = 2
    ORDER = 3
    UNAVAILABLE = 4

    STATUS_CHOICES = [
        (UNCHECKED, 'Находится на проверке'),
        (SALE, 'Доступно для продажи'),
        (ORDER, 'Только под заказ'),
        (UNAVAILABLE, 'Недоступно для продажи'),
    ]

    title = models.CharField(verbose_name='Название', max_length=150)
    slug = models.SlugField(verbose_name='Название на английском', max_length=150, unique=True, null=True, default=None)
    description = models.CharField(verbose_name='Описание', max_length=250)

    price = models.DecimalField(verbose_name='Цена без скидки', max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(verbose_name='Цена со скидкой', max_digits=8, decimal_places=2, default=0.00)
    discount = models.PositiveSmallIntegerField(
        verbose_name='Скидка в %',
        validators=[MinValueValidator(0), MaxValueValidator(80)]
    )

    stock = models.PositiveSmallIntegerField(verbose_name='Количество букетов', default=0)

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=UNCHECKED,
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

    # декоратор для отмены всех сохранений в бд, если произошла ошибка
    @transaction.atomic
    def save(self, *args, **kwargs):
        """ Переводит поле title с ru на en и сохраняет в slug """

        # сохраняем для определения id
        super(Bouquet, self).save()

        # for translate slug
        if self.slug is None:
            import translators as ts
            translated_title = ts.google(self.title)
            self.slug = slugify(f'bouquet {translated_title} {self.id}')

        # расчеты flower и composition
        compositions = Bouquet.objects.get(id=self.id).bouquet_composition.all()
        for composition in compositions:
            flower = Flower.objects.get(id=composition.flower.id)

            # удаляем старое значение из общего количества цветов в букетах
            flower.stock_in_bouquets -= composition.total_count
            # присваиваем новое значение
            composition.total_count = self.stock * composition.count

            # прибавляем к количеству цветов в букете total_count
            flower.stock_in_bouquets += composition.total_count

            # сохраняем composition и flower, если весь запаса хватает
            if flower.whole_stock >= flower.stock_in_bouquets:
                composition.save()
                flower.save()
            else:
                raise Exception(f'На складе нет такого количества цветов {flower.title}, '
                                f'нельзя добавить такое количество - {self.stock} букетов')

        # рассчитываем цену со скидкой
        sale = (self.price / 100) * self.discount
        self.discount_price = self.price - sale
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
        Flower, verbose_name='Выбрать цветок',
        on_delete=models.PROTECT,
        db_column='flower',
        related_name='flower_composition',
    )
    # количество цветка в букете
    count = models.PositiveSmallIntegerField(verbose_name='Количество цветов', default=0)
    # общее количество цветов в букетах (количество букетов * количество цветка в букете)
    total_count = models.PositiveSmallIntegerField(
        verbose_name='Общее количество цветов в этом букете',
        default=0
    )

    def __str__(self):
        return f'Composition id {self.id}, flower - {self.flower.title}, доступное количество для продажи: {self.flower.stock_for_sale}'

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'

    def delete(self, *args, **kwargs):
        flowers = Flower.objects.get(id=self.flower.id)
        # удаляем значение из общего количества цветов в букетах
        flowers.stock_in_bouquets -= self.total_count
        flowers.save()
        super(CompositionOfTheBouquet, self).delete(*args, **kwargs)



