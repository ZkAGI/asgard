from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class UserRegistrationViewTest(TestCase):
    def test_user_registration(self):
        url = reverse("user-registration")
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_user_registration_missing_fields(self):
        url = reverse("user-registration")
        data = {}  # Missing required fields

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())

    def test_user_registration_invalid_email(self):
        url = reverse("user-registration")
        data = {
            "email": "invalid-email@example.com",  # Invalid email format
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)
        self.assertFalse(User.objects.filter(email="invalid-email").exists())

    def test_user_registration_existing_email(self):
        User.objects.create_user(
            email="test@example.com", username="existinguser", password="testpassword"
        )
        url = reverse("user-registration")
        data = {
            "email": "test@example.com",  # Email already exists
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_user_registration_missing_username(self):
        url = reverse("user-registration")
        data = {
            "email": "test@example.com",
            "password": "testpassword",  # Missing username
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())
