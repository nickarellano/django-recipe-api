from recipe.serializers import IngredientSerializer
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Ingredient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsAPITests(TestCase):
    """Test the public facing API endpoints for ingredients"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_is_required_to_access_ingredients(self):
        """Test that login is required to access the ingredients"""
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test the authenticated API endpoints for ingredients"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "john@example.com", "Testing123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_are_scoped_to_the_user(self):
        """Test that the ingredients list is scoped to the authenticated user"""
        other_user = get_user_model().objects.create_user(
            "jane@example.com", "Testing123"
        )
        Ingredient.objects.create(user=other_user, name="Vinegar")

        ingredient = Ingredient.objects.create(user=self.user, name="Tumeric")

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)

    def test_creating_ingredient_successfully(self):
        """Test creating a new ingredient"""
        ingredient_data = {"name": "Cabbage"}

        response = self.client.post(INGREDIENTS_URL, ingredient_data)

        exists = Ingredient.objects.filter(
            user=self.user, name=ingredient_data["name"]
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_creating_ingredient_invalid(self):
        """Test that the name is required when creating an ingredient"""
        ingredient_data = {"name": ""}
        response = self.client.post(INGREDIENTS_URL, ingredient_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
