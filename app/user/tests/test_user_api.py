from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            "email": "john@example.com",
            "password": "Testing123",
            "name": "John Example",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            "email": "john@example.com",
            "password": "Testing123",
            "name": "John Doe",
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            "email": "john@example.com",
            "password": "pass",
            "name": "John Doe",
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "john@example.com",
            "password": "Testing123",
            "name": "John Doe",
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        user_data = {
            "email": "john@example.com",
            "password": "Testing123",
        }
        create_user(**user_data)
        payload = user_data.update({"password": "invalid"})
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_a_user(self):
        """Test that token is not created if user doesn't exist"""
        user_data = {
            "email": "john@example.com",
            "password": "Testing123",
        }
        response = self.client.post(TOKEN_URL, user_data)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_password(self):
        """Test that email and password are required"""
        user_data = {
            "email": "john@example.com",
            "password": "Testing123",
        }
        response = self.client.post(TOKEN_URL, user_data.update({"password": ""}))

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
