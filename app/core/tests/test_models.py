from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "john@example.com"
        password = "testing"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self):
        """Test the email for a new user is normalized"""
        email = "john@EXAMPLE.COM"
        user = get_user_model().objects.create_user(email, "testing")

        self.assertEqual(user.email, email.lower())