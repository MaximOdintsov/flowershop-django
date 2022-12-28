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
        category = ProductCategory.objects.get(slug='flowers')
        component_1 = ProductComponent.objects.get(slug='chamomile')
        component_2 = ProductComponent.objects.get(slug='red-roze')

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
        Checking calculate ProductComposition price:
        1. When changing ProductComposition.quantity
        2. ------""----- ProductComponent.price
        ============================================
        Add:
        """
        pass

    def test_calculate_product_price(self):
        """
        Checking calculate product price:
        1. When adding ProductComposition to products
        2. When changing ProductComposition.price
        3. ------""----- Product.discount
        =============================================
        Add:
        """
        pass

    def test_update_quantity_productcomponent(self):
        """
        Checking update quantity_in_product and quantity_for_sale in ProductComponent
        1. Update quantity when product.save()
        2. ---------““--------- ProductComposition.save()
        3. ---------““--------- OrderItem.save()
           if Order.order_status = STATUS_WAITING_FOR_PAYMENT or STATUS_PAID
        """
        pass
