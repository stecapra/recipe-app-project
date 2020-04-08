from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()


	def test_login_required(self):
		res = self.client.get(INGREDIENTS_URL)

		self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateIngredientsApiTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			email = 'test@example.com',
			password = '123123'
		)
		self.client = APIClient()
		self.client.force_authenticate(self.user)


	def test_retrieve_ingredients_list(self):
		Ingredient.objects.create(user = self.user, name = 'Cucamber')
		Ingredient.objects.create(user = self.user, name = 'Zucchini')

		res = self.client.get(INGREDIENTS_URL)

		ingredients = Ingredient.objects.all().order_by('-name')
		serializer = IngredientSerializer(ingredients, many = True)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)


	def test_ingredients_limited_to_user(self):
		u = get_user_model().objects.create_user(email = 'test1@example.com', password = '123123')
		Ingredient.objects.create(user = u, name = 'Zucchini')
		
		ingredient = Ingredient.objects.create(user = self.user, name = 'Broccoli')

		res = self.client.get(INGREDIENTS_URL)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(len(res.data), 1)
		self.assertEqual(res.data[0]['name'], ingredient.name)


	def test_create_ingredient_succesfull(self):
		payload = {'name': 'Zucchini'}

		self.client.post(INGREDIENTS_URL, payload)

		exists = Ingredient.objects.all().filter(
			user = self.user,
			name = payload['name']
		).exists()

		self.assertTrue(exists)


	def test_create_ingredient_invalid(self):
		payload = {'name': ''}

		res = self.client.post(INGREDIENTS_URL, payload)

		self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)











