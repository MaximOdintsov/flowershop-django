from django.test import TestCase

from django.core.files import File

from django.contrib.auth import get_user_model

User = get_user_model()


class UsersModelsTest(TestCase):

    def test_category_model_save_and_retrieve(self):
        user_1 = Category(
            ='Alex',
            slug='flower_1',
        )
        user_1.save()

        # add category_2
        superuser_1 = Category(
            name='Цветы_2',
            slug='flower_2',
        )
        superuser_1.save()

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