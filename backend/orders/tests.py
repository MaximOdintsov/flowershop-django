from django.test import TestCase

from .models import Order, OrderItem
from products.models import (ProductComposition,
                             ProductComponent,
                             Product,)

from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataBase(TestCase):
    fixtures = [
        "orders/fixtures/orders.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='maxim')

    def test_user_exists(self):
        users = User.objects.all()
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 1)
        self.assertEqual(user.username, 'maxim')
        self.assertTrue(user.is_superuser)

    def test_user_check_password(self):
        self.assertTrue(self.user.check_password('vevahu51'))

    def test_order_data(self):
        self.assertGreater(Order.objects.all().count(), 0)
        self.assertGreater(OrderItem.objects.all().count(), 0)

        self.assertGreater(ProductComponent.objects.all().count(), 0)
        self.assertGreater(Product.objects.all().count(), 0)
        self.assertGreater(ProductComposition.objects.all().count(), 0)

