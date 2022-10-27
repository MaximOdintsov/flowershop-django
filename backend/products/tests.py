from django.test import TestCase
from .models import Category, Flower

from django.core.files import File


# Create your tests here.


class ProductsModelsTest(TestCase):

    def test_category_model_save_and_retrieve(self):
        # add category_1
        category_1 = Category(
            name='Цветы_1',
            slug='flower_1',
        )
        category_1.save()

        # add category_2
        category_2 = Category(
            name='Цветы_2',
            slug='flower_2',
        )
        category_2.save()

        all_categories = Category.objects.all()

        # check: there must be 2 objects
        self.assertEqual(len(all_categories), 2)

        # checking the 1st element
        # check: name db == saved name
        self.assertEqual(
            all_categories[0].name, category_1.name,
        )
        # check: slug db == saved slug
        self.assertEqual(
            all_categories[0].slug, category_1.slug,
        )

        # checking the 2nd element
        # check: name db == saved name
        self.assertEqual(
            all_categories[1].name, category_2.name,
        )
        # check: slug db == saved slug
        self.assertEqual(
            all_categories[1].slug, category_2.slug,
        )

    # def test_flower_model_save_and_retrieve(self):
        # add flower_1
        flower_1 = Flower(
            category=category_1,
            title="Роза",
            slug="Roze",
            description="Белая роза",
            price=1000,
            discount=10,
            image=File(open('products/img/1.jpg', 'rb')),
            stock=4,
        )
        flower_1.save()

        # add flower_2
        flower_2 = Flower(
            category=category_2,
            title="Тюльпан",
            slug="Tulpan",
            description="Красивый тюльпанчик",
            price=1300,
            discount=0,
            image=File(open('products/img/2.jpg', 'rb')),
            stock=0,
        )
        flower_2.save()

        # upload all images from db
        all_flowers = Flower.objects.all()

        # check: there must be 2 objects
        self.assertEqual(len(all_flowers), 2)

        # checking the 1st element
        # check: category db == saved category
        self.assertEqual(
            all_flowers[0].category, flower_1.category,
        )
        # check: title db == saved title
        self.assertEqual(
            all_flowers[0].title, flower_1.title,
        )
        # check: slug db == saved slug
        self.assertEqual(
            all_flowers[0].slug, flower_1.slug,
        )
        # check: description db == saved description
        self.assertEqual(
            all_flowers[0].description, flower_1.description,
        )
        # check: price db == saved price
        self.assertEqual(
            all_flowers[0].price, flower_1.price,
        )
        # check: discount db == saved discount
        self.assertEqual(
            all_flowers[0].discount, flower_1.discount,
        )
        # check: the image from the db is equal to the saved image
        self.assertEqual(
            all_flowers[0].image, flower_1.image,
        )
        # check: stock db == saved stock
        self.assertEqual(
            all_flowers[0].stock, flower_1.stock,
        )

        # checking the 2nd element
        # check: category db == saved category
        self.assertEqual(
            all_flowers[1].category, flower_2.category,
        )
        # check: title db == saved title
        self.assertEqual(
            all_flowers[1].title, flower_2.title,
        )
        # check: slug db == saved slug
        self.assertEqual(
            all_flowers[1].slug, flower_2.slug,
        )
        # check: description db == saved description
        self.assertEqual(
            all_flowers[1].description, flower_2.description,
        )
        # check: price db == saved price
        self.assertEqual(
            all_flowers[1].price, flower_2.price,
        )
        # check: discount db == saved discount
        self.assertEqual(
            all_flowers[1].discount, flower_2.discount,
        )
        # check: the image from the db is equal to the saved image
        self.assertEqual(
            all_flowers[1].image, flower_2.image,
        )
        # check: stock db == saved stock
        self.assertEqual(
            all_flowers[1].stock, flower_2.stock,
        )

