from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Bouquet


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

    def counter(self, bouquet_id):
        try:
            cart = self.cart[bouquet_id]['quantity']
            if cart is None:
                return 0
            else:
                return cart
        except Exception:
            return 0

    def add(self, bouquet, quantity=1, update_quantity=False):
        """
        Добавляем продукт в корзину или обновляем его количество.
        """
        bouquet_id = str(bouquet.id)

        if bouquet_id not in self.cart:
            self.cart[bouquet_id] = {'quantity': 0,
                                     'price': str(bouquet.discount_price)}

        if update_quantity is True:
            self.cart[bouquet_id]['quantity'] = quantity
        else:
            self.cart[bouquet_id]['quantity'] = quantity

        if self.cart[bouquet_id]['quantity'] >= 0:
            self.save()
        else:
            raise ValidationError('Это значение не должно быть отрицательным')

    def add_one(self, bouquet, quantity=1, update_quantity=False):
        """
        Добавляем продукт в корзину или обновляем его количество.
        """
        bouquet_id = str(bouquet.id)

        if bouquet_id not in self.cart:
            self.cart[bouquet_id] = {'quantity': 0,
                                     'price': str(bouquet.discount_price)}

        if update_quantity is True:
            self.cart[bouquet_id]['quantity'] += quantity
        else:
            self.cart[bouquet_id]['quantity'] = quantity

        if self.cart[bouquet_id]['quantity'] >= 0:
            self.save()
        else:
            raise ValidationError('Это значение не должно быть отрицательным')

    def save(self):
        # Обновляем сессию cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отмечаем сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, bouquet):
        """
        Удаляем товар из корзины.
        """
        bouquet_id = str(bouquet.id)
        if bouquet_id in self.cart:
            del self.cart[bouquet_id]
            self.save()

    def __iter__(self):
        """
        Перебираем элементы в корзине и получаем продукты из базы данных.
        """
        bouquet_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        bouquets = Bouquet.objects.filter(id__in=bouquet_ids)
        for bouquet in bouquets:
            self.cart[str(bouquet.id)]['bouquet'] = bouquet

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчитываем все товары в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчитываем стоимость товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity']
                   for item in self.cart.values())

    def clear(self):
        """
        Удаляем корзину из сессии.
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True