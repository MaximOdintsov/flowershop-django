from decimal import Decimal

from django.test import TestCase

from .models import Order, OrderItem
from products.models import (ProductComposition,
                             ProductComponent,
                             Product, )
from django.utils import timezone


from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataBase(TestCase):
    fixtures = [
        "orders/fixtures/orders.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='maxim')

        self.product_1 = Product.objects.get(title='Ромашка')
        self.product_2 = Product.objects.get(title='Букет из ромашек')
        self.product_3 = Product.objects.get(title='Букет из ромашек и роз')

    def test_get_data(self):
        self.assertGreater(ProductComponent.objects.all().count(), 0)
        self.assertGreater(Product.objects.all().count(), 2)
        self.assertGreater(ProductComposition.objects.all().count(), 0)
        self.assertGreater(User.objects.all().count(), 0)

    def test_user_exists(self):
        users = User.objects.all()
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 1)
        self.assertEqual(user.username, 'maxim')
        self.assertTrue(user.is_superuser)

    def test_user_check_password(self):
        self.assertTrue(self.user.check_password('vevahu51'))

    def cart_number(self):
        cart_number = Order.objects.filter(user=self.user,
                                           order_status=Order.STATUS_CART
                                           ).count()
        return cart_number

    def test_function_cart(self):
        """
        Checking quantity carts:
        1. No cart
        2. Create cart
        3. Delete cart
        ==============
        Add: @staticmethod Order.get_cart(user: User)
        """

        # 1. No cart
        self.assertEqual(self.cart_number(), 0)

        # 2. Create cart
        Order.get_cart(self.user)
        self.assertEqual(self.cart_number(), 1)

        # 3. Delete cart
        Order.get_cart(self.user)
        self.assertEqual(self.cart_number(), 1)

    def test_cart_older_7_days(self):
        """
        If cart older than 7 days, it must be deleted:
        1. Get cart and make it older
        """

        # 1. Get cart and make it older
        cart = Order.get_cart(self.user)
        cart.creation_time = timezone.now() - timezone.timedelta(8)
        cart.save()

        cart = Order.get_cart(self.user)
        self.assertEqual((timezone.now() - cart.creation_time).days, 0)

    def test_price_setting_for_orderitem(self):
        """
        Checking to set price to product for orderitem:
        1. When saving orderitem
        2. When product price is changes
        ================================
        Add: @receiver orderitem_price_setting()
             Product.save_orderitem()
             @receiver Product.resave_related_order_items_after_save()
        """

        # 1. When saving orderitem
        cart = Order.get_cart(self.user)
        item = OrderItem.objects.create(id=5000, order=cart, product=self.product_3, quantity=1)
        self.assertEqual(item.price, self.product_3.discount_price)

        # 2. When product price is changes
        component = ProductComponent.objects.get(title='Ромашка')
        component.price = Decimal(1000)
        component.save()

        product = Product.objects.get(title='Букет из ромашек и роз')
        item = OrderItem.objects.get(id=5000)

        self.assertEqual(item.price, product.discount_price)

    def test_order_amount_recalculation_after_changed_orderitem(self):
        """
        Checking cart price:
        1. Getting the order amount before any changes
        2. -----------""----------- after adding items
        3. -----------""----------- after deleting 1 item
        4. -----------""----------- after deleting items
        =================================================
        Add: @property Orderitem.amount
             Order.get_amount()
             @receiver recalculate_order_amount_after_save()
             @receiver recalculate_order_amount_after_delete()
        """

        # 1. Getting the order amount before any changes
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))

        # 2. -----------""----------- after adding items
        i_1 = OrderItem.objects.create(order=cart, product=self.product_1, quantity=2)
        i_2 = OrderItem.objects.create(order=cart, product=self.product_2, quantity=5)
        i_3 = OrderItem.objects.create(order=cart,  product=self.product_3, quantity=4)
        amount = (self.product_1.discount_price * 2) + (self.product_2.discount_price * 5) +\
                 (self.product_3.discount_price * 4)

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(amount))

        # 3. -----------""----------- after deleting 1 item
        i_3.delete()
        amount = (self.product_1.discount_price * 2) + (self.product_2.discount_price * 5)

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(amount))

        # 4. -----------""----------- after deleting all items
        i_1.delete()
        i_2.delete()
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))

    def test_cart_status_changing_after_applying_make_order(self):
        """
        Checking cart status change after Order.make_order():
        1. Attempt to change the status for an empty cart
        2. ---------------""--------------- a non-empty cart
        ====================================================
        Add: Order.make_order()
        """

        # 1. Attempt to change the status for an empty cart
        cart = Order.get_cart(self.user)
        cart.make_order()
        self.assertEqual(cart.order_status, Order.STATUS_CART)

        # 2. ---------------""--------------- a non-empty cart
        OrderItem.objects.create(order=cart, product=self.product_1, quantity=2)
        cart.make_order()
        self.assertEqual(cart.order_status, Order.STATUS_WAITING_FOR_PAYMENT)

    def test_method_get_amount_of_unpaid_orders(self):
        """
        Checking @staticmethod get_amount_of_unpaid_orders() for several cases:
        1. Before creating cart
        2. After creating cart
        3. After cart.make_order()
        4. After order is paid
        5. After delete all orders
        ==========================
        Add: Order.get_amount_of_unpaid_orders(user: User)
        """

        # 1. Before creating cart
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(1535))

        # 2. After creating cart
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.product_1, quantity=2)

        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(1535))

        # 3. After cart.make_order()
        cart.make_order()
        order = cart
        amount_all_unpaid_orders = (self.product_1.discount_price * 2) + Decimal(1535)

        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(amount_all_unpaid_orders))

        # 4. After order is paid
        order.order_status = Order.STATUS_PAID
        order.save()

        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(1535))

        # 5. After delete all orders
        Order.objects.all().delete()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))
