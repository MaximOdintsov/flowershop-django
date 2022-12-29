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
        self.product_empty = Product.objects.get(slug='empty-bouquet')

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
        Checking if ProductComposition.recalculate_composition_price
        is calculated correctly:
        1. When saving ProductComposition
        2. When changing ProductComponent.price
        ============================================
        Add: @property ProductComposition.recalculate_composition_price
        """

        # 1. When saving ProductComposition
        composition = ProductComposition.objects.create(product=self.product,
                                                        component=self.component_1,
                                                        quantity=1)
        self.assertEqual(composition.recalculate_composition_price, self.component_1.price)

        # 2. When changing ProductComponent.price
        self.assertEqual(self.component_1.price, Decimal(100))
        self.assertEqual(self.component_2.price, Decimal(200))

        self.component_1.price = Decimal(2)
        self.component_2.price = Decimal(6)
        self.component_1.save()
        self.component_2.save()

        self.composition_1 = ProductComposition.objects.get(id=3)
        self.composition_2 = ProductComposition.objects.get(id=2)
        price_1 = 2 * self.composition_1.quantity
        price_2 = 6 * self.composition_2.quantity

        self.assertEqual(self.composition_1.recalculate_composition_price, price_1)
        self.assertEqual(self.composition_2.recalculate_composition_price, price_2)

    def test_calculate_product_price(self):
        """
        Checking calculate product price:
        1. When ProductComposition adding to products
        2. When changing ProductComposition.quantity
        3. ------""----- ProductComponent.price
        4. ------""----- Product.discount
        =============================================
        Add: @property Product.get_price
             @receiver(sender=ProductComposition) recalculate_price_and_new_price_product_after_save()
             @property Product.get_new_price
             @receiver(sender=Product) recalculate_new_price()

        """

        #  1. When ProductComposition adding to products
        self.assertEqual(self.product_empty.price, Decimal(0))
        composition_1 = ProductComposition.objects.create(id=4,
                                                          product=self.product_empty,
                                                          component=self.component_1,
                                                          quantity=1)
        composition_2 = ProductComposition.objects.create(id=5,
                                                          product=self.product_empty,
                                                          component=self.component_2,
                                                          quantity=1)

        product_empty = Product.objects.get(slug='empty-bouquet')
        self.assertEqual(product_empty.price, Decimal(100*1 + 200*1))

        # 2. When changing ProductComposition.quantity
        composition_1.quantity = 2
        composition_2.quantity = 3
        composition_1.save()
        composition_2.save()

        product_empty = Product.objects.get(slug='empty-bouquet')
        self.assertEqual(product_empty.price, Decimal(100 * 2 + 200 * 3))

        # 3. ------""----- ProductComponent.price
        self.component_1.price = Decimal(4)
        self.component_2.price = Decimal(5)
        self.component_1.save()
        self.component_2.save()

        product_empty = Product.objects.get(slug='empty-bouquet')
        price = (4 * 2) + (5 * 3)

        self.assertEqual(product_empty.price, price)

        # 4. ------""----- Product.discount
        product_empty.discount = 10
        product_empty.save()

        self.assertEqual(product_empty.new_price, Decimal('20.70'))

    def test_update_productcomponent_quantity_in_product_and_quantity_for_sale(self):
        """
        Checking:
        1. Updates quantity_in_product when Product.save()
        2. ---------------““--------------- ProductComposition.save()
        """
        pass

    def test_update_productcomponent_total_count_and_new_arrival(self):
        """
        Checking:
        1. Updates total_count when new_arrival is added
        2. new_arrival is reset to zero after adding to total_count
        3. quantity_in_product recalculated
        """
        pass


