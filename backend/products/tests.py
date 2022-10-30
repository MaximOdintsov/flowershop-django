from django.test import TestCase
from .models import Category, Flower, Bouquet
from .models import GalleryFlower

from django.core.files import File


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

    def test_flower_model_save_and_retrieve(self):
        # add category 1
        category_1 = Category(
            name='Цветы_1',
            slug='flower_1',
        )
        category_1.save()
        # add category 2
        category_2 = Category(
            name='Цветы_2',
            slug='flower_2',
        )
        category_2.save()

        # add flower_1
        flower_1 = Flower(
            category=Category.objects.all()[0],
            title="Роза",
            slug="Roze",
            description="Белая роза",
            price=1000,
            discount=10,
            # image=File(open('products/img/1.jpg', 'rb')),
            stock=4,
            available=True,
        )
        flower_1.save()

        # add flower_2
        flower_2 = Flower(
            category=Category.objects.all()[1],
            title="Тюльпан",
            slug="Tulpan",
            description="Красивый тюльпанчик",
            price=1300,
            discount=0,
            # image=File(open('products/img/2.jpg', 'rb')),
            stock=0,
            available=False,
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
        # self.assertEqual(
        #     all_flowers[0].image, flower_1.image,
        # )

        # check: stock db == saved stock
        self.assertEqual(
            all_flowers[0].stock, flower_1.stock,
        )
        # check: available db == saved available
        self.assertEqual(
            all_flowers[0].available, flower_1.available,
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
        # self.assertEqual(
        #     all_flowers[1].image, flower_2.image,
        # )
        # check: stock db == saved stock

        self.assertEqual(
            all_flowers[1].stock, flower_2.stock,
        )
        # check: available db == saved available
        self.assertEqual(
            all_flowers[1].available, flower_2.available,
        )

    def test_bouquet_model_save_and_retrieve(self):
        # add bouquet_1
        bouquet_1 = Bouquet(
            title="Букет из 100 роз",
            slug="buket_iz_100_roz",
            description="Красивый букет из разных видов роз",
            price=15.000,
            discount=10,
            # image=File(open('products/img/1.jpg', 'rb')),
            stock=3,
            available=True,
            only_on_order=False,
        )
        bouquet_1.save()

        # add bouquet_2
        bouquet_2 = Bouquet(
            title="Свадебный букет",
            slug="svadebny_buket",
            description="Свадебный букет из тюльпанов",
            price=7000,
            discount=0,
            stock=1,
            available=False,
            only_on_order=True,
        )
        bouquet_2.save()

        # upload all images from db
        all_bouquets = Bouquet.objects.all()

        # check: there must be 2 objects
        self.assertEqual(len(all_bouquets), 2)

        # checking the 1st element
        # check: title db == saved title
        self.assertEqual(
            all_bouquets[0].title, bouquet_1.title,
        )
        # check: slug db == saved slug
        self.assertEqual(
            all_bouquets[0].slug, bouquet_1.slug,
        )
        # check: description db == saved description
        self.assertEqual(
            all_bouquets[0].description, bouquet_1.description,
        )
        # check: price db == saved price
        self.assertEqual(
            all_bouquets[0].price, bouquet_1.price,
        )
        # check: discount db == saved discount
        self.assertEqual(
            all_bouquets[0].discount, bouquet_1.discount,
        )
        # check: stock db == saved stock
        self.assertEqual(
            all_bouquets[0].stock, bouquet_1.stock,
        )
        # check: available db == saved available
        self.assertEqual(
            all_bouquets[0].available, bouquet_1.available,
        )
        # check: only_on_order db == saved only_on_order
        self.assertEqual(
            all_bouquets[0].only_on_order, bouquet_1.only_on_order,
        )

        # checking the 2nd element
        # check: title db == saved title
        self.assertEqual(
            all_bouquets[1].title, bouquet_2.title,
        )
        # check: slug db == saved slug
        self.assertEqual(
            all_bouquets[1].slug, bouquet_2.slug,
        )
        # check: description db == saved description
        self.assertEqual(
            all_bouquets[1].description, bouquet_2.description,
        )
        # check: price db == saved price
        self.assertEqual(
            all_bouquets[1].price, bouquet_2.price,
        )
        # check: discount db == saved discount
        self.assertEqual(
            all_bouquets[1].discount, bouquet_2.discount,
        )
        # check: stock db == saved stock
        self.assertEqual(
            all_bouquets[1].stock, bouquet_2.stock,
        )
        # check: available db == saved available
        self.assertEqual(
            all_bouquets[1].available, bouquet_2.available,
        )
        # check: only_on_order db == saved only_on_order
        self.assertEqual(
            all_bouquets[1].only_on_order, bouquet_2.only_on_order,
        )
