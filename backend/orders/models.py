import datetime

from django.utils import timezone

from django.db import models
from products.models import Product, ProductComposition

from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    RECEIPT_CHOICES = [
        (1, 'Самовывоз'),
        (2, 'Доставка курьером'),
    ]
    PAYMENT_CHOICES = [
        (1, 'Наличные'),
        (2, 'Безналичные'),
        (3, 'Онлайн оплата'),
    ]
    READINESS_CHOICES = [
        (1, 'Принят'),
        (2, 'Готовится'),
        (3, 'Готов')
    ]

    user = models.ForeignKey(User,
                             verbose_name='Клиент',
                             on_delete=models.CASCADE,
                             related_name='order_user',
                             blank=True, null=True)
    price = models.DecimalField('Цена всего заказа',
                                max_digits=8,
                                decimal_places=2,
                                default=0,
                                null=True,
                                blank=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)

    phone = PhoneNumberField('Номер телефона', region='RU')
    email = models.EmailField('Электронная почта', null=True, blank=True)
    address = models.CharField('Адрес получения заказа',
                               max_length=100,
                               null=True,
                               blank=True)

    create = models.DateTimeField('Время создания заказа', default=timezone.now)
    update = models.DateTimeField('Время выполнения заказа', null=True, blank=True)
    ready_time = models.TimeField('Время готовности', null=True, blank=True)

    receipt = models.PositiveSmallIntegerField('Способ получения',
                                               choices=RECEIPT_CHOICES)
    payment_method = models.PositiveSmallIntegerField('Способ оплаты',
                                                      choices=PAYMENT_CHOICES)
    paid = models.BooleanField('Оплачен', default=False)
    received = models.BooleanField('Получен', default=False)
    readiness_status = models.PositiveSmallIntegerField('Статус готовности',
                                                        choices=READINESS_CHOICES,
                                                        default=1)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['id']

    def __str__(self):
        return f'Заказ №{self.id}'

    def check_readiness_status(self):
        """
        Сохраняет Заказ в БД,
        проверяет статус готовности
        """
        super(Order, self).save()
        if self.readiness_status == 3:
            return True
        else:
            return False

    def update_date(self):
        """
        Обновляет дату завершенного заказа
        """
        self.update = timezone.now()

    def return_ready_time(self):
        """
        Рассчитывает, за какое время был собран заказ
        """
        seconds = (self.update - self.create).seconds

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 3600) % 60

        time = datetime.time(hours, minutes, seconds)
        return time

    def delete_order_items(self):
        """
        Удаляет все компоненты заказа
        """
        items = OrderItem.objects.filter(order_id=self.id)

        for item in items:
            item.delete()

    def save(self, *args, **kwargs):
        if self.check_readiness_status() is True:
            self.update_date()
            self.ready_time = self.return_ready_time()

        super(Order, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.delete_order_items()
        super(Order, self).delete(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              on_delete=models.CASCADE,
                              related_name='order')
    product = models.ForeignKey(Product,
                                verbose_name='Товар',
                                on_delete=models.PROTECT,
                                related_name='order_item_product')
    quantity = models.PositiveSmallIntegerField('Количество товара в заказе', default=1)
    old_quantity = models.PositiveSmallIntegerField('Старое количество товара', default=0)
    price = models.DecimalField('Цена товара в заказе', max_digits=8,
                                decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def check_quantity_update(self):
        """
        Проверяет, было ли обновлено self.quantity
        """
        if self.old_quantity != self.quantity:
            return True
        else:
            return False

    def update_quantity_components(self):
        """
        Обновляет количество компонентов на складе при добавлении товара в заказ
        """
        compositions = ProductComposition.objects.filter(product_composition_id=self.product.id)
        for composition in compositions:
            composition.component_composition.total_count += self.old_quantity * composition.quantity
            composition.component_composition.total_count -= self.quantity * composition.quantity
            composition.component_composition.save()

    def update_order_price(self):
        """
        Обновляем значение цены заказа
        """
        self.order.price -= self.price
        self.price = 0

        self.price = self.product.discount_price * self.quantity
        self.order.price += self.price

        self.order.save()

    def delete_quantity_components(self):
        """
        Прибавляет количество компонентов на складе при удалении товара из заказа
        """
        compositions = ProductComposition.objects.filter(product_composition_id=self.product.id)
        for composition in compositions:
            composition.component_composition.total_count += self.old_quantity * composition.quantity
            composition.component_composition.save()

    def delete_order_price(self):
        """
        Обновляем цену заказа при удалении продукта из заказа
        """
        self.order.price -= self.price
        self.order.save()

    def save(self, *args, **kwargs):

        if self.check_quantity_update() is True:
            self.update_quantity_components()
            self.old_quantity = self.quantity

        self.update_order_price()

        super(OrderItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.delete_quantity_components()
        self.delete_order_price()
        super(OrderItem, self).delete(*args, **kwargs)
