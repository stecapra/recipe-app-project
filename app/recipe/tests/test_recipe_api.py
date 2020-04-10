from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe, Tag, Ingredient


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
	return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main Course'):
	return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Zucchini'):
	return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
	defaults = {
		'title': 'Test recipe',
		'time_minutes': 10,
		'price': 5.00
	}
	defaults.update(params)

	return Recipe.objects.create(user = user, **defaults)


class PublicRecipeApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()


	def test_auth_required(self):
		res = self.client.get(RECIPE_URL)

		self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateRecipeApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = get_user_model().objects.create_user(
			email = 'test@exmaple.com',
			password = '123123'
		)

		self.client.force_authenticate(self.user)


	def test_retrieve_recipes(self):
		sample_recipe(user = self.user)
		sample_recipe(user = self.user)
		
		res = self.client.get(RECIPE_URL)
		recipes = Recipe.objects.all().order_by('-id')
		
		serializer = RecipeSerializer(recipes, many=True)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)


	def test_recipes_limited_to_user(self):
		u = get_user_model().objects.create_user(
			email = 'test1@example.com',
			password = '123123'
		)

		sample_recipe(user = u)
		sample_recipe(user = self.user)

		res = self.client.get(RECIPE_URL)

		recipes = Recipe.objects.filter(user = self.user)
		serializer = RecipeSerializer(recipes, many=True)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(len(res.data), len(serializer.data))
		self.assertEqual(res.data, serializer.data)


	def test_view_recipe_detail(self):
		recipe = sample_recipe(user=self.user)
		recipe.tags.add(sample_tag(user=self.user))
		recipe.ingredients.add(sample_ingredient(user=self.user))

		url = detail_url(recipe.id)

		res = self.client.get(url)
		serializer = RecipeDetailSerializer(recipe)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)


	def test_create_basic_recipe(self):
		payload = {'title': 'Title', 'time_minutes': 100, 'price': 5}

		res = self.client.post(RECIPE_URL, payload)

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)

		recipe = Recipe.objects.get(id=res.data['id'])
		for key in payload.keys():
			self.assertEqual(payload[key], getattr(recipe, key))


	def test_create_recipe_with_tag(self):
		tag1 = sample_tag(user = self.user, name = 'Vegan')
		tag2 = sample_tag(user = self.user, name = 'Dessert')

		payload = {
			'title': 'Title',
			'price': 5,
			'time_minutes': 500,
			'tags': [tag1.id, tag2.id]
		}
		res = self.client.post(RECIPE_URL, payload)

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)

		recipe = Recipe.objects.get(id=res.data['id'])
		tags = recipe.tags.all()

		self.assertEqual(tags.count(), 2)
		self.assertIn(tag1, tags)
		self.assertIn(tag2, tags)


	def test_create_recipe_with_ingredients(self):
		ingr1 = sample_ingredient(user=self.user, name = 'Ing1')
		ingr2 = sample_ingredient(user=self.user, name = 'Ing2')

		payload = {
			'title': 'Title',
			'price': 5,
			'time_minutes': 500,
			'ingredients': [ingr1.id, ingr2.id] 
		}

		res = self.client.post(RECIPE_URL, payload)

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)

		recipe = Recipe.objects.get(id=res.data['id'])
		ingredients = recipe.ingredients.all()

		self.assertEqual(ingredients.count(), 2)
		self.assertIn(ingr1, ingredients)
		self.assertIn(ingr2, ingredients)














