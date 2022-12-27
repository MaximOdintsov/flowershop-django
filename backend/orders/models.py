import datetime
from decimal import Decimal

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from django.db import models
from products.models import Product, ProductComposition

from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):

    STATUS_WAITING_FOR_PAYMENT = 1
    STATUS_PAID = 2
    STATUS_CART = 3
    STATUS_CANCELED = 4
    STATUS_CHOICES = [
        (STATUS_WAITING_FOR_PAYMENT, 'Ожидает оплату'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_CART, 'Корзина'),
        (STATUS_CANCELED, 'Заказ отменен')
    ]
    RECEIPT_PICKUP = 1
    RECEIPT_DELIVERY = 2
    RECEIPT_CHOICES = [
        (RECEIPT_PICKUP, 'Самовывоз'),
        (RECEIPT_DELIVERY, 'Доставка курьером'),
    ]
    PAYMENT_CASH = 1
    PAYMENT_CARD = 2
    PAYMENT_ONLINE = 3
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Наличные'),
        (PAYMENT_CARD, 'Безналичные'),
        (PAYMENT_ONLINE, 'Онлайн оплата')
    ]
    READINESS_ACCEPTED = 1
    READINESS_PREPARING = 2
    READINESS_READY = 3
    READINESS_RECEIVED = 4
    READINESS_CHOICES = [
        (READINESS_ACCEPTED, 'Принят'),
        (READINESS_PREPARING, 'Готовится'),
        (READINESS_READY, 'Готов'),
        (READINESS_RECEIVED, 'Получен')
    ]

    user = models.ForeignKey(User, verbose_name='Клиент', on_delete=models.CASCADE, null=True, blank=True)

    amount = models.DecimalField('Цена заказа', max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    receipt_method = models.PositiveSmallIntegerField('Способ получения', choices=RECEIPT_CHOICES, null=True, blank=True)
    payment_method = models.PositiveSmallIntegerField('Способ оплаты', choices=PAYMENT_CHOICES, null=True, blank=True)
    order_status = models.PositiveSmallIntegerField('Статус заказа', choices=STATUS_CHOICES, default=STATUS_CART)
    readiness_status = models.PositiveSmallIntegerField('Статус готовности', choices=READINESS_CHOICES, null=True, blank=True)
    creation_time = models.DateTimeField('Время создания заказа', default=timezone.now)

    first_name = models.CharField('Имя', max_length=150, blank=True, null=True)
    phone = PhoneNumberField('Номер телефона', region='RU', blank=True, null=True)
    email = models.EmailField('Электронная почта', blank=True, null=True)
    address = models.CharField('Адрес получения заказа', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['readiness_status', 'creation_time']

    def __str__(self):
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

    def make_order(self):
        items = self.orderitem_set.all()
        if items and self.order_status == self.STATUS_CART:
            self.order_status = self.STATUS_WAITING_FOR_PAYMENT
            self.save()

    @staticmethod
    def get_amount_of_unpaid_orders(user: User):
        amount = Order.objects.filter(user=user,
                                      order_status=Order.STATUS_WAITING_FOR_PAYMENT,
                                      ).aggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField('Количество в заказе', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'Товар заказа №{self.order.id} - "{self.product.title}" '

    @property
    def amount(self):
        return self.quantity * self.price


@receiver(pre_save, sender=OrderItem)
def orderitem_price_setting(sender, instance, **kwargs):
    instance.price = instance.product.discount_price


@receiver(post_save, sender=OrderItem)
def recalculate_order_amount_after_save(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()


@receiver(post_delete, sender=OrderItem)
def recalculate_order_amount_after_delete(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()

















    # def update_quantity_components(self):
    #     """
    #     Обновляет количество компонентов на складе при добавлении товара в заказ
    #     """
    #     compositions = ProductComposition.objects.filter(product_composition_id=self.product.id)
    #     for composition in compositions:
    #         composition.component_composition.total_count += self.old_quantity * composition.quantity
    #         composition.component_composition.total_count -= self.quantity * composition.quantity
    #         composition.component_composition.save()
    #
    # def update_order_price(self):
    #     """
    #     Обновляем значение цены заказа
    #     """
    #     self.order.price -= self.price
    #     self.price = 0
    #
    #     self.price = self.product.discount_price * self.quantity
    #     self.order.price += self.price
    #
    #     self.order.save()
    #
    # def delete_quantity_components(self):
    #     """
    #     Прибавляет количество компонентов на складе при удалении товара из заказа
    #     """
    #     compositions = ProductComposition.objects.filter(product_composition_id=self.product.id)
    #     for composition in compositions:
    #         composition.component_composition.total_count += self.old_quantity * composition.quantity
    #         composition.component_composition.save()
    #
    # def delete_order_price(self):
    #     """
    #     Обновляем цену заказа при удалении продукта из заказа
    #     """
    #     self.order.price -= self.price
    #     self.order.save()
    #
    # def save(self, *args, **kwargs):
    #
    #     self.update_quantity_components()
    #     self.update_order_price()
    #
    #     super(OrderItem, self).save(*args, **kwargs)
    #
    # def delete(self, *args, **kwargs):
    #     self.delete_quantity_components()
    #     self.delete_order_price()
    #     super(OrderItem, self).delete(*args, **kwargs)









# class Order(models.Model):
#     PICKUP = 1
#     DELIVERY = 2
#     RECEIPT_CHOICES = [
#         (PICKUP, 'Самовывоз'),
#         (DELIVERY, 'Доставка курьером'),
#     ]
#
#     CASH = 1
#     CARD = 2
#     ONLINE = 3
#     PAYMENT_CHOICES = [
#         (CASH, 'Наличные'),
#         (CARD, 'Безналичные'),
#         (ONLINE, 'Онлайн оплата'),
#     ]
#
#     ACCEPTED = 1
#     PREPARING = 2
#     READY = 3
#     READINESS_CHOICES = [
#         (ACCEPTED, 'Принят'),
#         (PREPARING, 'Готовится'),
#         (READY, 'Готов')
#     ]
#
#     user = models.ForeignKey(User,
#                              verbose_name='Клиент',
#                              on_delete=models.CASCADE,
#                              related_name='order_user',
#                              blank=True, null=True)
#     price = models.DecimalField('Цена всего заказа',
#                                 max_digits=8,
#                                 decimal_places=2,
#                                 default=0,
#                                 null=True,
#                                 blank=True)
#     first_name = models.CharField('Имя', max_length=150, blank=True)
#
#     phone = PhoneNumberField('Номер телефона', region='RU')
#     email = models.EmailField('Электронная почта', null=True, blank=True)
#     address = models.CharField('Адрес получения заказа',
#                                max_length=100,
#                                null=True,
#                                blank=True)
#
#     create = models.DateTimeField('Время создания заказа', default=timezone.now)
#     update = models.DateTimeField('Время выполнения заказа', null=True, blank=True)
#     ready_time = models.TimeField('Время готовности', null=True, blank=True)
#
#     receipt = models.PositiveSmallIntegerField('Способ получения',
#                                                choices=RECEIPT_CHOICES)
#     payment_method = models.PositiveSmallIntegerField('Способ оплаты',
#                                                       choices=PAYMENT_CHOICES)
#     paid = models.BooleanField('Оплачен', default=False)
#     received = models.BooleanField('Получен', default=False)
#     readiness_status = models.PositiveSmallIntegerField('Статус готовности',
#                                                         choices=READINESS_CHOICES,
#                                                         default=ACCEPTED)
#
#     class Meta:
#         verbose_name = 'Заказ'
#         verbose_name_plural = 'Заказы'
#         ordering = ['id']
#
#     def __str__(self):
#         return f'Заказ №{self.id}'
#
#     def check_readiness_status(self):
#         """
#         Сохраняет Заказ в БД,
#         проверяет статус готовности
#         """
#         super(Order, self).save()
#         if self.readiness_status == 3:
#             return True
#         else:
#             return False
#
#     def update_date(self):
#         """
#         Обновляет дату завершенного заказа
#         """
#         self.update = timezone.now()
#
#     def return_ready_time(self):
#         """
#         Рассчитывает, за какое время был собран заказ
#         """
#         seconds = (self.update - self.create).seconds
#
#         hours = seconds // 3600
#         minutes = (seconds % 3600) // 60
#         seconds = (seconds % 3600) % 60
#
#         time = datetime.time(hours, minutes, seconds)
#         return time
#
#     def delete_order_items(self):
#         """
#         Удаляет все компоненты заказа
#         """
#         items = OrderItem.objects.filter(order_id=self.id)
#
#         for item in items:
#             item.delete()
#
#     def save_only(self):
#         super(Order, self).save()
#
#     def save(self, *args, **kwargs):
#         if self.check_readiness_status() is True:
#             self.update_date()
#             self.ready_time = self.return_ready_time()
#
#         super(Order, self).save(*args, **kwargs)
#
#     def delete(self, *args, **kwargs):
#         self.delete_order_items()
#         super(Order, self).delete(*args, **kwargs)
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order,
#                               verbose_name='Заказ',
#                               on_delete=models.CASCADE,
#                               related_name='order')
#     product = models.ForeignKey(Product,
#                                 verbose_name='Товар',
#                                 on_delete=models.PROTECT,
#                                 related_name='order_item_product')
#     quantity = models.PositiveSmallIntegerField('Количество товара в заказе', default=1)
#     old_quantity = models.PositiveSmallIntegerField('Старое количество товара', default=0)
#     price = models.DecimalField('Цена товара в заказе', max_digits=8,
#                                 decimal_places=2, default=0)
#
#     class Meta:
#         verbose_name = 'Товар'
#         verbose_name_plural = 'Товары'
#
#     def __str__(self):
#         return f'Товар заказа "{self.product.title}" '
#
#     def check_quantity_update(self):
#         """
#         Проверяет, было ли обновлено self.quantity
#         """
#         if self.old_quantity != self.quantity:
#             return True
#         else:
#             return False
#
#     def update_quantity_components(self):
#         """
#         Обновляет количество компонентов на складе при добавлении товара в заказ
#         """
#         compositions = ProductComposition.objects.filter(product_composition_id=self.product.id)
#         for composition in compositions:
#             composition.component_composition.total_count += self.old_quantity * composition.quantity
#             composition.component_composition.total_count -= self.quantity * composition.quantity
#             composition.component_composition.save()
#
#     def update_order_price(self):
#         """
#         Обновляем значение цены заказа
#         """
#         self.order.price -= self.price
#         self.price = 0
#
#         self.price = self.product.discount_price * self.quantity
#         self.order.price += self.price
#
#         self.order.save_only()
#
#     def delete_quantity_components(self):
#         """
#         Прибавляет количество компонентов на складе при удалении товара из заказа
#         """
#         compositions = ProductComposition.objects.filter(product_composition_id=self.product.id)
#         for composition in compositions:
#             composition.component_composition.total_count += self.old_quantity * composition.quantity
#             composition.component_composition.save()
#
#     def delete_order_price(self):
#         """
#         Обновляем цену заказа при удалении продукта из заказа
#         """
#         self.order.price -= self.price
#         self.order.save()
#
#     def save(self, *args, **kwargs):
#
#         if self.check_quantity_update() is True:
#             self.update_quantity_components()
#             self.old_quantity = self.quantity
#
#         self.update_order_price()
#
#         super(OrderItem, self).save(*args, **kwargs)
#
#     def delete(self, *args, **kwargs):
#         self.delete_quantity_components()
#         self.delete_order_price()
#         super(OrderItem, self).delete(*args, **kwargs)
