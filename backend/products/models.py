from decimal import Decimal

from django.db.models import Q
from django.utils.text import slugify

import translators as ts

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver


def get_translated_slug(self):

    try:
        if (self.slug == str(self.id)) or (self.slug is None):
            translated_title = ts.google(self.title, 'ru', 'en')
            slug = slugify(translated_title)
            if slug:
                self.slug = slug
            else:
                raise Exception()
    except Exception:
        slug = self.id
        self.slug = slug


class ProductCategory(models.Model):
    title = models.CharField('Имя категории', max_length=100)
    slug = models.SlugField('Название на английском', max_length=150, unique=True, null=True)
    show_in_filter = models.BooleanField('Показывать в фильтре', default=False)

    class Meta:
        verbose_name = 'Категория продукта'
        verbose_name_plural = 'Категории продуктов'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(ProductCategory, self).save()
        get_translated_slug(self)
        super(ProductCategory, self).save()


class ProductComponent(models.Model):
    title = models.CharField('Название', max_length=150)
    slug = models.SlugField('Название на английском', max_length=150, unique=True, null=True)

    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    new_arrival = models.PositiveSmallIntegerField('Новое поступление', default=0)
    quantity_in_stock = models.PositiveSmallIntegerField('Запас', default=0)
    quantity_of_sold = models.PositiveSmallIntegerField('Количество проданных', default=0)

    available = models.BooleanField(verbose_name='Доступен', default=False)
    show_in_filter = models.BooleanField(verbose_name='Показывать в фильтре', default=False)

    class Meta:
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'
        unique_together = ('slug', )
        ordering = ['quantity_of_sold']

    def __str__(self):
        return self.title

    def save_related_productcompositions(self):
        """Saves all related ProductComposition when ProductComponent.price changes"""
        compositions = self.productcomposition_set.all()
        for composition in compositions:
            composition.save()

    def add_new_arrival(self):
        self.quantity_in_stock += self.new_arrival
        self.new_arrival = 0

    def save(self, *args, **kwargs):
        super(ProductComponent, self).save()
        get_translated_slug(self)
        super(ProductComponent, self).save()


@receiver(pre_save, sender=ProductComponent)
def recalculate_quantity_in_stock_before_save(sender, instance, **kwargs):
    component = instance
    component.add_new_arrival()


@receiver(post_save, sender=ProductComponent)
def save_productcomposition(sender, instance, **kwargs):
    component = instance
    component.save_related_productcompositions()


class Product(models.Model):
    STATUS_REVIEW = 1
    STATUS_AVAILABLE = 2
    STATUS_ONLY_ORDER = 3
    STATUS_UNAVAILABLE = 4
    STATUS_CHOICES = [
        (STATUS_REVIEW, 'На проверке'),
        (STATUS_AVAILABLE, 'Доступно'),
        (STATUS_ONLY_ORDER, 'Только под заказ'),
        (STATUS_UNAVAILABLE, 'Недоступно')
    ]

    category = models.ForeignKey(ProductCategory, verbose_name='Категория', on_delete=models.PROTECT)

    title = models.CharField('Название', max_length=150)
    slug = models.SlugField('Название на английском', max_length=150, unique=True, null=True)
    preview = models.ImageField('Превью', upload_to='products/previews')

    price = models.DecimalField('Цена без скидки', max_digits=10, decimal_places=2, default=0)
    discount = models.PositiveSmallIntegerField('Скидка в %', default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    new_price = models.DecimalField('Цена со скидкой', max_digits=10, decimal_places=2, default=0)

    status = models.PositiveSmallIntegerField('Статус', choices=STATUS_CHOICES, default=STATUS_REVIEW)

    header_title = models.TextField('Заголовок в поиске', null=True, blank=True)
    header_description = models.TextField('Описание продукта в поиске', null=True, blank=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        unique_together = ('slug', 'id')
        ordering = ['status']

    def __str__(self):
        return f'{self.title} - доступно: {self.get_available_quantity_of_products}'

    @property
    def get_price(self):
        price = Decimal(0)
        for composition in self.productcomposition_set.all():
            price += composition.get_composition_price
        return price

    @property
    def get_new_price(self):
        return (self.price/100) * (100-self.discount)

    @property
    def get_available_quantity_of_products(self):
        compositions = self.productcomposition_set.all()
        number_of_composition_available = []

        for composition in compositions:
            if composition.quantity > 0:
                quantity = composition.component.quantity_in_stock // composition.quantity
                number_of_composition_available.append(quantity)

        if number_of_composition_available:
            return min(number_of_composition_available)
        return 0

    @property
    def get_status(self):
        if self.get_available_quantity_of_products > 0:
            return self.STATUS_AVAILABLE
        else:
            return self.STATUS_ONLY_ORDER

    @property
    def get_productcomponent_status(self):
        compositions = self.productcomposition_set.all()
        for composition in compositions:
            if composition.component.available is False:
                return False
        return True

    def save_orderitem(self):
        items = self.orderitem_set.all()
        for item in items:
            item.save()

    def save(self, *args, **kwargs):
        super(Product, self).save()
        get_translated_slug(self)
        super(Product, self).save()


@receiver(pre_save, sender=Product)
def recalculate_new_price(sender, instance, **kwargs):
    product = instance
    product.new_price = product.get_new_price


@receiver(post_save, sender=Product)
def save_orderitem_after_save(sender, instance, **kwargs):
    product = instance
    product.save_orderitem()


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    image = models.ImageField('Изображение', upload_to='products/images')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class ProductComposition(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    component = models.ForeignKey(ProductComponent, verbose_name='Выбрать цветок', on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField('Количество компонентов', default=0)

    class Meta:
        verbose_name = 'Состав'

    def __str__(self):
        return f'{self.component} composition for {self.product}'

    @property
    def get_composition_price(self):
        return self.quantity * self.component.price


@receiver(post_save, sender=ProductComposition)
def save_product_after_save(sender, instance, **kwargs):
    product = instance.product
    product.price = product.get_price

    if product.get_productcomponent_status is False:
        product.status = Product.STATUS_UNAVAILABLE
    else:
        product.status = product.get_status
    product.save()


@receiver(post_delete, sender=ProductComposition)
def save_product_after_delete(sender, instance, **kwargs):
    product = instance.product
    product.price = product.get_price
    product.status = product.get_status
    product.save()


# def save_slug(pk, slug, title):
#     """
#     Переводит поле title с ru на en и сохраняет в slug
#     """
#
#     if (slug == str(pk)) or (len(slug) == 0):
#         try:
#             import translators as ts
#             translated_title = ts.google(title)
#             slug = slugify(translated_title)
#             return slug
#         except Exception:
#             slug = pk
#             return slug
#     else:
#         return slug