from decimal import Decimal
from django.test import TestCase

from .models import ProductCategory, ProductComponent, Product, ProductComposition

from django.core.files import File
from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataBase(TestCase):
    fixtures = [
        "products/fixtures/products.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='maxim')
        self.category = ProductCategory.objects.get(slug='flowers')
        self.component_1 = ProductComponent.objects.get(slug='chamomile')
        self.component_2 = ProductComponent.objects.get(slug='red-roze')
        self.composition_1 = ProductComposition.objects.get(id=3)
        self.composition_2 = ProductComposition.objects.get(id=2)
        self.product = Product.objects.get(slug='bouquet-of-roses-and-daisies')
        self.product_empty = Product.objects.create(category=self.category,
                                                    title='empty',
                                                    slug='empty',
                                                    preview='/backend/products/img/1.jpg',
                                                    status=Product.STATUS_AVAILABLE)

    def test_data(self):
        components = ProductComponent.objects.all().count()
        categories = ProductCategory.objects.all().count()
        products = Product.objects.all().count()
        compositions = ProductComposition.objects.all().count()

        self.assertGreater(components, 1)
        self.assertGreater(categories, 0)
        self.assertGreater(products, 0)
        self.assertGreater(compositions, 0)

    def test_calculate_productcomposition_price(self):
        """
        Checking if ProductComposition.get_composition_price is calculated correctly:
        1. When saving ProductComposition
        2. When changing ProductComponent.price

        ============================================
        Add: @property ProductComposition.get_composition_price
        """

        # 1. When saving ProductComposition
        composition = ProductComposition.objects.create(product=self.product_empty, quantity=1,
                                                          component=self.component_1)
        self.assertEqual(composition.get_composition_price, self.component_1.price)

        # 2. When changing ProductComponent.price
        self.assertEqual(self.component_1.price, Decimal(100))
        self.assertEqual(self.component_2.price, Decimal(200))

        self.component_1.price = Decimal(2)
        self.component_2.price = Decimal(6)
        self.component_1.save()
        self.component_2.save()

        composition_1 = ProductComposition.objects.get(id=3)
        composition_2 = ProductComposition.objects.get(id=2)
        price_1 = 2 * composition_1.quantity
        price_2 = 6 * composition_2.quantity

        self.assertEqual(composition_1.get_composition_price, price_1)
        self.assertEqual(composition_2.get_composition_price, price_2)

    def test_calculate_product_price(self):
        """
        Checking calculate product price:
        1. When ProductComposition adding to products
        2. When changing ProductComposition.quantity
        3. ------""----- ProductComponent.price
        4. ------""----- Product.discount
        5. When ProductComposition removing

        =============================================
        Add: @property Product.get_price
             @receiver(sender=ProductComposition) save_product()

             @property Product.get_new_price
             @receiver(sender=Product) recalculate_new_price()
             ProductComponent.save_related_productcompositions()
             @receiver(sender=ProductComponent) save_productcomposition()
        """

        #  1. When ProductComposition adding to products
        self.assertEqual(self.product_empty.price, Decimal(0))
        composition_1 = ProductComposition.objects.create(product=self.product_empty, quantity=1,
                                                          component=self.component_1)
        composition_2 = ProductComposition.objects.create(product=self.product_empty, quantity=1,
                                                          component=self.component_2)

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.price, Decimal(100*1 + 200*1))

        # 2. When changing ProductComposition.quantity
        composition_1.quantity = 2
        composition_2.quantity = 1
        composition_1.save()
        composition_2.save()

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.price, Decimal(100 * 2 + 200 * 1))

        # 3. ------""----- ProductComponent.price
        self.component_1.price = Decimal(10)
        self.component_2.price = Decimal(20)
        self.component_1.save()
        self.component_2.save()

        product_empty = Product.objects.get(slug='empty')
        price = (10 * 2) + (20 * 1)

        self.assertEqual(product_empty.price, price)

        # 4. ------""----- Product.discount
        product_empty.discount = 10
        product_empty.save()

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.new_price, Decimal(36))

        # 5. Price recalculation when removing ProductComposition
        self.assertEqual(composition_1.get_composition_price, Decimal(20))
        self.assertEqual(product_empty.discount, 10)
        composition_1.delete()
        price = Decimal(40) - Decimal(20)

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.discount, 0)
        self.assertEqual(product_empty.price, price)

    def test_update_productcomponent_quantity(self):
        """
        Checking:
        1. Updates ProductComponent.quantity_in_stock when ProductComponent.new_arrival changes
        2. Product.status change if ProductComponent.quantity_in_stock is not enough
        3. Product.status change if ProductComponent.quantity_in_stock is enough
        4. Product.status change if ProductComponent.quantity_in_stock has been changed

        ====================================================================================================
        Add: ProductComponent.add_new_arrival()
             @receiver(sender=ProductComponent) recalculate_quantity_in_stock_before_save()
             @property Product.get_available_quantity_of_products
             Product.get_status()
             @receiver(sender=ProductComposition) save_product()
        """

        # 1. Updates ProductComponent.quantity_in_stock when ProductComponent.new_arrival changes
        self.assertEqual(self.component_1.quantity_in_stock, 100)

        self.component_1.new_arrival = 10
        self.component_1.save()

        self.assertEqual(self.component_1.new_arrival, 0)
        self.assertEqual(self.component_1.quantity_in_stock, 110)

        # 2. Product.status change if ProductComponent.quantity_in_stock is not enough
        self.assertEqual(self.component_1.quantity_in_stock, 110)
        self.assertEqual(self.component_2.quantity_in_stock, 100)
        self.assertEqual(self.product_empty.status, Product.STATUS_AVAILABLE)

        composition_1 = ProductComposition.objects.create(product=self.product_empty, quantity=500,
                                                          component=self.component_1)
        composition_2 = ProductComposition.objects.create(product=self.product_empty, quantity=20,
                                                          component=self.component_2)

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.get_available_quantity_of_products, 0)
        self.assertEqual(product_empty.status, Product.STATUS_ONLY_ORDER)

        # 3. Product.status change if ProductComponent.quantity_in_stock is enough
        composition_1.quantity = 10
        composition_2.quantity = 10
        composition_1.save()
        composition_2.save()

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.get_available_quantity_of_products, 10)
        self.assertEqual(product_empty.status, Product.STATUS_AVAILABLE)

        # 4. Product.status change if ProductComponent.quantity_in_stock has been changed
        self.component_1.quantity_in_stock = 21
        self.component_2.quantity_in_stock = 2
        self.component_1.save()
        self.component_2.save()

        product_empty = Product.objects.get(slug='empty')
        self.assertEqual(product_empty.get_available_quantity_of_products, 0)
        self.assertEqual(product_empty.status, Product.STATUS_ONLY_ORDER)
