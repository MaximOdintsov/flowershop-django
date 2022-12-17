from django.utils import timezone

from django.db import models
from products.models import Product

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
        (3, 'Готов. Ожидает доставку'),
        (4, 'Получен клиентом')
    ]

    user = models.ForeignKey(User,
                             verbose_name='Клиент',
                             on_delete=models.CASCADE,
                             related_name='order_user',
                             blank=True, null=True  )
    price = models.DecimalField('Цена всего заказа',
                                max_digits=8,
                                decimal_places=2,
                                default=0,
                                null=True,
                                blank=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)

    phone = PhoneNumberField('Номер телефона', region='RU')
    email = models.EmailField('Электронная почта', null=True, blank=True)
    address = models.CharField('Адрес получения заказа',
                               max_length=100,
                               null=True,
                               blank=True)

    create = models.DateTimeField('Время создания заказа', default=timezone.now)
    update = models.DateTimeField('Время выполнения заказа', default=timezone.now)

    receipt = models.PositiveSmallIntegerField('Способ получения',
                                               choices=RECEIPT_CHOICES)
    payment_method = models.PositiveSmallIntegerField('Способ оплаты',
                                                      choices=PAYMENT_CHOICES)
    paid = models.BooleanField('Оплачен', default=False)
    readiness_status = models.PositiveSmallIntegerField('Статус готовности',
                                                        choices=READINESS_CHOICES,
                                                        default=1)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def update_date(self, *args, **kwargs):
        self.update = timezone.now()
        Order.save(update_fields=['update'])

    def save(self, *args, **kwargs):

        if self.readiness_status == 3:
            Order.update = timezone.now()

        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    product = models.ForeignKey(Product,
                                verbose_name='Товар',
                                on_delete=models.CASCADE,
                                related_name='order_item_product')
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              on_delete=models.CASCADE,
                              related_name='order')
    quantity = models.IntegerField('Количество товара', default=1)
    price_item = models.DecimalField('Цена 1 товара', max_digits=8,
                                     decimal_places=2, default=0)
    price = models.DecimalField('Общая цена', max_digits=8,
                                decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        # удаляем старое значение из цены и обнуляем
        self.order.price -= self.price_item
        self.price_item = 0

        # создаем новое значение и добавляем к общей цене
        self.price_item = self.product.discount_price * self.quantity
        self.order.price += self.price_item

        self.order.save()

        super(OrderItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.order.price -= self.price_item
        self.order.save()
        super(OrderItem, self).delete(*args, **kwargs)
