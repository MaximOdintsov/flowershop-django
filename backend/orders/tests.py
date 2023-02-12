from decimal import Decimal

from django.test import TestCase

from .models import Order, OrderItem, PromoCode
from products.models import (ProductComposition,
                             ProductComponent,
                             Product)
from django.utils import timezone


from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataBase(TestCase):
    fixtures = [
        "orders/fixtures/orders.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='maxim')
        self.component_1 = ProductComponent.objects.get(slug='red-roze')
        self.component_2 = ProductComponent.objects.get(slug='chamomile')
        self.product_1 = Product.objects.get(slug='bouquet-of-roses-and-daisies')
        self.product_2 = Product.objects.get(slug='bouquet-of-chamomile')
        self.promocode_1 = PromoCode.objects.create(id=1, code='СКИДКА10', discount=10)

    def test_get_data(self):
        self.assertGreater(ProductComponent.objects.all().count(), 0)
        self.assertGreater(Product.objects.all().count(), 1)
        self.assertGreater(ProductComposition.objects.all().count(), 0)
        self.assertGreater(User.objects.all().count(), 0)
        self.assertGreater(PromoCode.objects.all().count(), 0)

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
                                           order_status=Order.STATUS_CART).count()
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
        2. When ProductComponent.price is changes
        3. When ProductComposition.quantity is changes
        ================================
        Add: @receiver orderitem_price_setting()
             Product.save_orderitem()
             @receiver Product.save_orderitem_after_save()
        """

        # 1. When saving orderitem
        cart = Order.get_cart(self.user)
        item = OrderItem.objects.create(id=1000, order=cart, product=self.product_1, quantity=1)
        self.assertEqual(item.price, self.product_1.new_price)

        # 2. When ProductComponent.price is changes
        self.component_1.price = Decimal(10)
        self.component_1.save()

        item = OrderItem.objects.get(id=1000)
        self.assertEqual(item.price, Decimal(1100))

        # 3. When ProductComposition.quantity is changes
        product = Product.objects.get(slug='bouquet-of-roses-and-daisies')
        composition = product.productcomposition_set.all()[0]
        self.assertEqual(composition.quantity, 10)

        composition.quantity = 20
        composition.save()

        item = OrderItem.objects.get(id=1000)
        self.assertEqual(item.price, Decimal(2100))

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
        amount = (self.product_1.new_price * 2) + (self.product_2.new_price * 5)

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(amount))

        # 3. -----------""----------- after deleting 1 item
        i_1.delete()
        amount = (self.product_2.new_price * 5)

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(amount))

        # 4. -----------""----------- after deleting all items
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
        self.assertEqual(cart.order_status, Order.STATUS_PENDING_CONFIRMATION)

    def test_recalculation_of_the_quantity_of_components_after_make_order(self):
        """
        Checking:
        1. If Order.order_status == STATUS_PENDING_CONFIRMATION,
           ProductComponent.quantity_in_stock and quantity_of_sold should not be recalculated
        2. If Order.order_status == STATUS_CONFIRMED,
           ProductComponent.quantity_in_stock and quantity_of_sold must be recalculated
        3. If Order.order_status == STATUS_CANCELED,
           ProductComponent.quantity_in_stock and quantity_of_sold should return back
        4. If Order.delete() when Order.order_status == STATUS_CANCELED,
           ProductComponent.quantity_in_stock and quantity_of_sold don't change
        5. If Order.delete() when Order.order_status == STATUS_CONFIRMED,
           ProductComponent.quantity_in_stock and quantity_of_sold should return back
        =======================================================================================
        Add: Order.recalculate_components_quantity()
             Order.save_for_models()
             @receiver(sender=Order) recalculate_component_quantity_and_set_amount_before_save()
             @receiver(sender=Order) recalculate_component_quantity_before_delete()
        """

        # 1. If Order.order_status == STATUS_PENDING_CONFIRMATION,
        #    ProductComponent.quantity_in_stock and quantity_of_sold should not be recalculated
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.product_1, quantity=1)
        OrderItem.objects.create(order=cart, product=self.product_2, quantity=2)
        self.assertEqual(self.component_1.quantity_in_stock, 100)
        self.assertEqual(self.component_1.quantity_of_sold, 0)
        self.assertEqual(self.component_2.quantity_in_stock, 100)
        self.assertEqual(self.component_2.quantity_of_sold, 0)
        cart.make_order()

        order = cart
        order.order_status = Order.STATUS_PENDING_CONFIRMATION
        order.save()

        component_1 = ProductComponent.objects.get(slug='red-roze')
        component_2 = ProductComponent.objects.get(slug='chamomile')
        self.assertEqual(component_1.quantity_in_stock, 100)
        self.assertEqual(component_1.quantity_of_sold, 0)
        self.assertEqual(component_2.quantity_in_stock, 100)
        self.assertEqual(component_2.quantity_of_sold, 0)

        # 2. If Order.order_status == STATUS_CONFIRMED,
        #    ProductComponent.quantity_in_stock and quantity_of_sold must be recalculated
        order.order_status = Order.STATUS_CONFIRMED
        order.save()
        self.assertEqual(order.update_component_flag, True)

        component_1 = ProductComponent.objects.get(slug='red-roze')
        component_2 = ProductComponent.objects.get(slug='chamomile')
        self.assertEqual(component_1.quantity_in_stock, 90)
        self.assertEqual(component_1.quantity_of_sold, 10)
        self.assertEqual(component_2.quantity_in_stock, 70)
        self.assertEqual(component_2.quantity_of_sold, 30)

        # 3. If Order.order_status == STATUS_CANCELED,
        #    ProductComponent.quantity_in_stock and quantity_of_sold should return back
        order.order_status = Order.STATUS_CANCELED
        order.save()
        self.assertEqual(order.update_component_flag, False)

        component_1 = ProductComponent.objects.get(slug='red-roze')
        component_2 = ProductComponent.objects.get(slug='chamomile')
        self.assertEqual(component_1.quantity_in_stock, 100)
        self.assertEqual(component_1.quantity_of_sold, 0)
        self.assertEqual(component_2.quantity_in_stock, 100)
        self.assertEqual(component_2.quantity_of_sold, 0)

        # 4. If Order.delete() when Order.order_status == STATUS_CANCELED,
        #    ProductComponent.quantity_in_stock and quantity_of_sold don't change

        order.delete()
        component_1 = ProductComponent.objects.get(slug='red-roze')
        component_2 = ProductComponent.objects.get(slug='chamomile')
        self.assertEqual(component_1.quantity_in_stock, 100)
        self.assertEqual(component_1.quantity_of_sold, 0)
        self.assertEqual(component_2.quantity_in_stock, 100)
        self.assertEqual(component_2.quantity_of_sold, 0)

        # 5. If Order.delete() when Order.order_status == STATUS_CONFIRMED,
        #    ProductComponent.quantity_in_stock and quantity_of_sold should return back
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.product_1, quantity=1)
        OrderItem.objects.create(order=cart, product=self.product_2, quantity=2)
        self.assertEqual(self.component_1.quantity_in_stock, 100)
        self.assertEqual(self.component_1.quantity_of_sold, 0)
        self.assertEqual(self.component_2.quantity_in_stock, 100)
        self.assertEqual(self.component_2.quantity_of_sold, 0)
        cart.make_order()

        order = cart
        order.order_status = Order.STATUS_CONFIRMED
        order.save()
        self.assertEqual(order.update_component_flag, True)

        order.delete()
        component_1 = ProductComponent.objects.get(slug='red-roze')
        component_2 = ProductComponent.objects.get(slug='chamomile')
        self.assertEqual(component_1.quantity_in_stock, 100)
        self.assertEqual(component_1.quantity_of_sold, 0)
        self.assertEqual(component_2.quantity_in_stock, 100)
        self.assertEqual(component_2.quantity_of_sold, 0)

    def test_changing_order_amount_when_price_product_changes(self):
        """
        1. Checking changing OrderItem.price when Product.price changes
        2. Checking changing Order.amount when Product.price changes
        3. Checking changing Order.amount when OrderItem deletes
        4. The price should not change if the order status is not CART and not PENDING_CONFIRMATION
        ===========================================================================================
        Change: OrderItem.save()
                @receiver(pre_save, sender=Order) recalculate_component_quantity_and_set_amount_before_save
        """

        # 1. Checking changing OrderItem.price when Product.price changes
        cart = Order.get_cart(self.user)
        item = OrderItem.objects.create(id=1000, order=cart, product=self.product_2, quantity=1)
        self.assertEqual(item.price, Decimal(900))

        self.component_2.price = 10
        self.component_2.save()

        item = OrderItem.objects.get(id=1000)
        self.assertEqual(item.price, Decimal(90))
        item.delete()

        # 2. Checking changing Order.amount when Product.price changes
        cart = Order.get_cart(self.user)
        item_1 = OrderItem.objects.create(order=cart, product=self.product_1, quantity=1)
        item_2 = OrderItem.objects.create(order=cart, product=self.product_2, quantity=1)

        self.assertEqual(cart.amount, Decimal(3900))
        self.component_1.price = 1
        self.component_2.price = 1
        self.component_1.save()
        self.component_2.save()

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(29))

        # 3. Checking changing Order.amount when OrderItem deletes
        item_1.delete()
        item_2.delete()

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))

        # 4. The price should not change if the order status is not CART and not PENDING_CONFIRMATION
        self.assertEqual(self.product_1.new_price, Decimal(3000))
        self.assertEqual(self.product_2.new_price, Decimal(900))

        OrderItem.objects.create(order=cart, product=self.product_1, quantity=1)
        OrderItem.objects.create(order=cart, product=self.product_2, quantity=1)
        self.assertEqual(cart.amount, Decimal(3900))

        self.assertEqual(cart.id, 7)
        self.assertEqual(cart.amount, Decimal(3900))
        cart.order_status = Order.STATUS_CONFIRMED
        cart.save()

        self.component_1.price = 1
        self.component_2.price = 1
        self.component_1.save()
        self.component_2.save()

        order = Order.objects.get(id=7)
        self.assertEqual(order.amount, Decimal(3900))

        order.order_status = Order.STATUS_CANCELED
        order = Order.objects.get(id=7)
        self.assertEqual(order.amount, Decimal(3900))

        order.order_status = Order.STATUS_PENDING_CONFIRMATION
        order.save()
        order = Order.objects.get(id=7)
        self.assertEqual(order.amount, Decimal(29))

        order.order_status = Order.STATUS_CART
        order.save()
        cart = Order.objects.get(id=7)
        self.assertEqual(cart.amount, Decimal(29))

    def test_applying_a_discount_to_an_order(self):
        """
        1. Promo code is valid when the validity period has started but not yet expired:
            1.1. When the product is not discounted
            1.2. When the product is discounted
        2. Promo code is not valid until the start of its action.
        3. Promo code is not valid after its expiration.
        4. Promo code cannot be reused
        5. New promo code should work
        ===============================================================================
        Extending the function OrderItem.amount()
        Add: Promocode.get_availability_status
             Promocode.save_orders()
             @receiver(sender=PromoCode) recalculate_order_amount_before_save()
        """

        # 1. Promo code is valid when the validity period has started but not yet expired:
        self.promocode_1.start_time = timezone.now()
        self.promocode_1.end_time = timezone.now() + timezone.timedelta(7)
        self.promocode_1.save()
        cart = Order.get_cart(self.user)

        # 1.1. When the product is not discounted
        self.assertEqual(self.product_1.discount, 0)
        self.assertEqual(self.product_1.new_price, Decimal(3000))

        OrderItem.objects.create(order=cart, product=self.product_1, quantity=1)
        self.assertEqual(cart.amount, Decimal(3000))
        self.assertEqual(self.promocode_1.discount, 10)
        cart.promo_code = self.promocode_1
        cart.save()

        self.assertEqual(cart.amount, Decimal(2700))

        # 1.2. When the product is discounted
        self.assertEqual(self.product_2.discount, 10)
        self.assertEqual(self.product_2.price, Decimal(1000))
        self.assertEqual(self.product_2.new_price, Decimal(900))
        OrderItem.objects.create(order=cart, product=self.product_2, quantity=1)

        self.assertTrue(self.promocode_1.get_availability_status)
        self.assertEqual(cart.amount, Decimal(3600))

        # 2. Promo code is not valid until the start of its action.
        self.promocode_1.valid_from = timezone.now() + timezone.timedelta(1)
        self.promocode_1.valid_to = timezone.now() + timezone.timedelta(8)
        self.promocode_1.save()

        cart = Order.get_cart(self.user)
        self.promocode_1 = PromoCode.objects.get(id=1)
        self.assertFalse(self.promocode_1.get_availability_status)
        self.assertEqual(cart.amount, Decimal(3900))

        # 3. Promo code is not valid after its expiration.
        self.promocode_1.valid_from = timezone.now() - timezone.timedelta(8)
        self.promocode_1.valid_to = timezone.now() - timezone.timedelta(1)
        self.promocode_1.save()
        cart = Order.get_cart(self.user)
        self.promocode_1 = PromoCode.objects.get(id=1)

        self.assertFalse(self.promocode_1.get_availability_status)
        self.assertEqual(cart.amount, Decimal(3900))

        cart.make_order()

        # 4. Promo code cannot be reused
        self.promocode_1.valid_from = timezone.now()
        self.promocode_1.valid_to = timezone.now() + timezone.timedelta(7)
        self.promocode_1.save()
        self.promocode_1 = PromoCode.objects.get(id=1)

        cart = Order.get_cart(self.user)
        self.assertEqual(self.product_1.new_price, Decimal(3000))
        OrderItem.objects.create(order=cart, product=self.product_1, quantity=2)

        self.assertEqual(cart.amount, Decimal(6000))
        self.assertEqual(self.promocode_1.discount, 10)

        if self.promocode_1.check_if_it_has_already_been_used(self.user, self.promocode_1):
            cart.promo_code = self.promocode_1
            cart.save()

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(6000))
        cart.make_order()

        # 5. New promo code should work
        promocode_2 = PromoCode.objects.create(id=2, code='ПРОМО20', discount=20, valid_from=timezone.now(), valid_to=(timezone.now()+timezone.timedelta(7)))
        cart = Order.get_cart(self.user)
        cart.make_order()

        self.assertEqual(self.product_1.discount, 0)
        self.assertEqual(self.product_1.new_price, Decimal(3000))
        self.assertEqual(self.product_2.discount, 10)
        self.assertEqual(self.product_2.price, Decimal(1000))
        self.assertEqual(self.product_2.new_price, Decimal(900))

        OrderItem.objects.create(order=cart, product=self.product_1, quantity=1)
        OrderItem.objects.create(order=cart, product=self.product_2, quantity=1)
        cart.promo_code = promocode_2
        cart.save()

        cart = Order.get_cart(self.user)
        self.assertTrue(promocode_2.get_availability_status)
        self.assertEqual(cart.amount, Decimal(3300))
