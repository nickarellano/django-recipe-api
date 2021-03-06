from django.contrib.auth import get_user_model
from recipe.serializers import TagSerializer
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from core.models import Tag

TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTests(TestCase):
    """Test the public tags API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authenticated tags API"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "john@example.com", "Testing123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that returned tags are scoped to the authenticated user"""
        other_user = get_user_model().objects.create_user(
            "jane@example.com", "Testing123"
        )
        Tag.objects.create(user=other_user, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        tag_data = {"name": "Test Tag"}
        self.client.post(TAGS_URL, tag_data)

        exists = Tag.objects.filter(user=self.user, name=tag_data["name"]).exists()

        self.assertTrue(exists)

    def create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        tag_data = {"name": ""}
        response = self.client.post(TAGS_URL, tag_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
