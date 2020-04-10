from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email = 'test@example.com', password = '123123'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_succesfull(self):
        """Test creating a new user with an email is succesfull"""
        email = 'spruzzi23@gmail.com'
        password = '123123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normilize(self):
        email = 'spruzzi23@GMAIL.COM'
        password = '123123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email.lower())


    def test_email_validation(self):
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user(
                None,
                '123123'
            )


    def test_create_new_useruser(self):
        user = get_user_model().objects.create_superuser(
            'spruzzi23@gmail.com',
            '123123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Vegan'
        )

        self.assertEqual(str(tag), tag.name)


    def test_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name = 'Cucamber'
        )

        self.assertEqual(str(ingredient), ingredient.name)


    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Title',
            time_minutes = 5,
            price = 5.80

        )

        self.assertEqual(str(recipe), recipe.title)












