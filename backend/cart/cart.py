from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Product

from django.views.decorators.http import require_POST


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session

        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def counter(self, product_id):
        try:
            cart = self.cart[product_id]['quantity']
            if cart is None:
                return 0
            else:
                return cart
        except Exception:
            return 0

    def add(self, product, quantity=1):
        """
        Добавляем продукт в корзину или обновляем его количество.
        """
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'old_price': str(product.price),
                                     'discount_price': str(product.discount_price)}

        self.cart[product_id]['quantity'] = quantity

        if self.cart[product_id]['quantity'] >= 0:
            self.save()
        else:
            raise ValidationError('Это значение не должно быть отрицательным')

    def add_one(self, product, quantity=1, update_quantity=False):
        """
        Добавляем продукт в корзину или обновляем его количество.
        """
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'old_price': str(product.price),
                                     'discount_price': str(product.discount_price)}

        if update_quantity is True:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id]['quantity'] = quantity

        if self.cart[product_id]['quantity'] >= 0:
            self.save()
        else:
            raise ValidationError('Это значение не должно быть отрицательным')

    def update_cart(self, product_ids):
        for product_id in product_ids:
            product = Product.objects.get(id=product_id)

            product_id = str(product_id)
            self.cart[product_id]['old_price'] = str(product.price)
            self.cart[product_id]['discount_price'] = str(product.discount_price)

    def save(self):
        # Обновляем сессию cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отмечаем сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product):
        """
        Удаляем товар из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебираем элементы в корзине и получаем продукты из базы данных.
        """
        product_ids = self.cart.keys()

        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['discount_price'] = Decimal(item['discount_price'])
            item['old_price'] = Decimal(item['old_price'])
            item['total_old_price'] = item['old_price'] * item['quantity']
            item['total_price'] = item['discount_price'] * item['quantity']

            yield item

    def __len__(self):
        """
        Подсчитываем все товары в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_old_price(self):
        """
        Подсчитываем стоимость товаров в корзине без скидки.
        """
        return sum(Decimal(item['old_price']) * item['quantity']
                   for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчитываем стоимость товаров в корзине.
        """
        return sum(Decimal(item['discount_price']) * item['quantity']
                   for item in self.cart.values())

    def clear(self):
        """
        Удаляем корзину из сессии.
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True