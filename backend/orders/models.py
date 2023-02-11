from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from django.db import models
from products.models import Product, ProductComposition

from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth import get_user_model

User = get_user_model()


class PromoCode(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    discount = models.PositiveSmallIntegerField('Скидка в %', default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    valid_from = models.DateTimeField('Действует с', default=timezone.now)
    valid_to = models.DateTimeField('Действует до', default=(timezone.now() + timezone.timedelta(7)))

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

    def __str__(self):
        return self.name

    @property
    def get_availability_status(self):
        if self.valid_from <= timezone.now() <= self.valid_to:
            return True
        else:
            return False

    @staticmethod
    def check_if_it_has_already_been_used(user: User, promo_code):
        for order in Order.objects.filter(user=user):
            if order.promo_code.id == promo_code.id:
                return False
        return True

    def save_orders(self):
        if self.id:
            for order in self.order_set.all():
                order.save()


@receiver(pre_save, sender=PromoCode)
def recalculate_order_amount_before_save(sender, instance, **kwargs):
    promo_code = instance
    promo_code.save_orders()


class Order(models.Model):
    STATUS_PENDING_CONFIRMATION = 1
    STATUS_CONFIRMED = 2
    STATUS_CART = 3
    STATUS_CANCELED = 4
    STATUS_CHOICES = [
        (STATUS_PENDING_CONFIRMATION, 'Ожидает подтверждения'),
        (STATUS_CONFIRMED, 'Подтвержден'),
        (STATUS_CART, 'Корзина'),
        (STATUS_CANCELED, 'Отменен')
    ]
    RECEIPT_PICKUP = 1
    RECEIPT_DELIVERY = 2
    RECEIPT_CHOICES = [
        (RECEIPT_PICKUP, 'Самовывоз'),
        (RECEIPT_DELIVERY, 'Доставка курьером'),
    ]
    PAYMENT_CASH = 1
    PAYMENT_CARD = 2
    PAYMENT_TRANSFER = 3
    PAYMENT_ONLINE = 4
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Оплата наличными'),
        (PAYMENT_CARD, 'Оплата картой'),
        (PAYMENT_TRANSFER, 'Перевод на карту'),
        (PAYMENT_ONLINE, 'Онлайн оплата')
    ]
    READINESS_PREPARING = 1
    READINESS_READY = 2
    READINESS_RECEIVED = 3
    READINESS_CHOICES = [
        (READINESS_PREPARING, 'Готовится'),
        (READINESS_READY, 'Готов'),
        (READINESS_RECEIVED, 'Получен')
    ]

    user = models.ForeignKey(User, verbose_name='Клиент', on_delete=models.CASCADE, null=True, blank=True)
    promo_code = models.ForeignKey(PromoCode, verbose_name='Промокод', on_delete=models.PROTECT, null=True, blank=True)

    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    receipt_method = models.PositiveSmallIntegerField('Способ получения', choices=RECEIPT_CHOICES, null=True, blank=True)

    payment_method = models.PositiveSmallIntegerField('Способ оплаты', choices=PAYMENT_CHOICES, null=True, blank=True)
    payment_state = models.BooleanField('Статус оплаты', default=False)

    order_status = models.PositiveSmallIntegerField('Статус заказа', choices=STATUS_CHOICES, default=STATUS_CART)
    readiness_status = models.PositiveSmallIntegerField('Статус готовности', choices=READINESS_CHOICES, null=True, blank=True)
    creation_time = models.DateTimeField('Время создания заказа', default=timezone.now)
    order_on_site = models.BooleanField('Заказ с сайта', default=False)

    update_component_flag = models.BooleanField('Флаг обновления компонента', default=False)

    first_name = models.CharField('Имя', max_length=150, blank=True, null=True)
    phone = PhoneNumberField('Номер телефона', region='RU', blank=True, null=True)
    email = models.EmailField('Электронная почта', blank=True, null=True)
    address = models.CharField('Адрес получения заказа', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['order_status', 'readiness_status', 'creation_time']

    def __str__(self):
        if self.order_status == self.STATUS_CART:
            return f'Корзина  №{self.id}'
        return f'Заказ №{self.id}'

    @staticmethod
    def get_cart(user: User):
        cart = Order.objects.filter(user=user,
                                    order_status=Order.STATUS_CART
                                    ).first()

        if cart and (timezone.now() - cart.creation_time).days > 7:
            cart.delete()
            cart = None
        if not cart:
            cart = Order.objects.create(user=user,
                                        order_status=Order.STATUS_CART,
                                        amount=0)
        return cart

    def get_amount(self):
        amount = Decimal(0)
        for item in self.orderitem_set.all():
            amount += item.amount
        return amount

    def get_old_amount(self):
        old_amount = Decimal(0)
        for item in self.orderitem_set.all():
            old_amount += item.old_amount
        return old_amount

    def make_order(self):
        items = self.orderitem_set.all()
        if items and self.order_status == self.STATUS_CART:
            self.order_status = self.STATUS_PENDING_CONFIRMATION
            self.save()

    def make_order_on_site(self):
        """Order placed on the site"""
        self.order_on_site = True
        self.save()

    def recalculate_components_quantity(self):

        if self.order_status == self.STATUS_PENDING_CONFIRMATION:
            self.update_component_flag = False

        elif self.order_status == self.STATUS_CONFIRMED:
            if self.update_component_flag is False:
                items = self.orderitem_set.all()
                for item in items:
                    compositions = item.product.productcomposition_set.all()
                    for composition in compositions:
                        component = composition.component

                        quantity = item.quantity * composition.quantity
                        component.quantity_in_stock -= quantity
                        component.quantity_of_sold += quantity
                        component.save()
                        self.update_component_flag = True

        elif self.order_status == self.STATUS_CANCELED:
            if self.update_component_flag is True:
                items = self.orderitem_set.all()
                for item in items:
                    compositions = item.product.productcomposition_set.all()
                    for composition in compositions:
                        component = composition.component

                        quantity = item.quantity * composition.quantity
                        component.quantity_in_stock += quantity
                        component.quantity_of_sold -= quantity
                        component.save()
                        self.update_component_flag = False

    @property
    def length_cart(self):
        length = 0
        for item in self.orderitem_set.all():
            length += item.quantity
        return length

    def save_for_models(self):
        super(Order, self).save()


@receiver(pre_save, sender=Order)
def recalculate_component_quantity_and_set_amount_before_save(sender, instance, **kwargs):
    order = instance
    if order.id:
        order.recalculate_components_quantity()

        if order.order_status == order.STATUS_CART or order.order_status == order.STATUS_PENDING_CONFIRMATION:
            order.amount = order.get_amount()
        else:
            ValidationError(f'Статус заказа не должен быть {order.order_status}')


@receiver(pre_delete, sender=Order)
def recalculate_component_quantity_before_delete(sender, instance, **kwargs):
    order = instance
    order.order_status = order.STATUS_CANCELED
    order.recalculate_components_quantity()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField('Количество в заказе', default=1)
    creation_time = models.DateTimeField('Время добавления товара', default=timezone.now)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'"{self.product.title}" '

    @property
    def get_status_product(self):
        return self.product.status

    @property
    def amount(self):
        amount = self.quantity * self.price

        if self.order.order_status == self.order.STATUS_CART or self.order.order_status == self.order.STATUS_PENDING_CONFIRMATION:
            if self.product.discount == 0 and self.order.promo_code and self.order.promo_code.get_availability_status is True:
                return (amount/100) * (100-self.order.promo_code.discount)
        return amount

    @property
    def old_amount(self):
        return self.quantity * self.product.price

    def save(self, *args, **kwargs):
        if self.order.order_status == self.order.STATUS_CART or self.order.order_status == self.order.STATUS_PENDING_CONFIRMATION:
            super(OrderItem, self).save(*args, **kwargs)
        else:
            ValidationError(f'Нельзя изменить заказ со статусом {self.order.order_status}')


@receiver(pre_save, sender=OrderItem)
def orderitem_price_setting(sender, instance, **kwargs):
    instance.price = instance.product.new_price


@receiver(post_save, sender=OrderItem)
def recalculate_order_amount_after_save(sender, instance, **kwargs):
    order = instance.order
    if order.order_status == order.STATUS_CART or order.order_status == order.STATUS_PENDING_CONFIRMATION:
        order.amount = order.get_amount()
        order.save_for_models()


@receiver(post_delete, sender=OrderItem)
def recalculate_order_amount_after_delete(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save_for_models()