from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserRegistrationViewTest(TestCase):
    def test_user_registration(self):
        url = reverse('user-registration')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_user_registration_missing_fields(self):
        url = reverse('user-registration')
        data = {}  # Missing required fields

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    def test_user_registration_invalid_email(self):
        url = reverse('user-registration')
        data = {
            'email': 'invalid-email@example.com',  # Invalid email format
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())

    def test_user_registration_existing_email(self):
        User.objects.create_user(email='test@example.com', username='existinguser', password='testpassword')
        url = reverse('user-registration')
        data = {
            'email': 'test@example.com',  # Email already exists
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_user_registration_missing_username(self):
        url = reverse('user-registration')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword'  # Missing username
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())



class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)

    def test_user_logout(self):
        url = reverse('user-logout')
        self.client.force_authenticate(user=self.user, token=self.token)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
