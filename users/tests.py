from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123'
        )

    def test_user_registration(self):
        """Тест регистрации пользователя"""
        # Используем action URL для регистрации
        url = reverse('user-register')
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)

    def test_user_profile_authenticated(self):
        """Тест получения профиля авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)
        # Используем action URL для профиля
        url = reverse('user-profile', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_owner(self):
        """Тест обновления профиля владельцем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_user_update_other_user(self):
        """Тест обновления профиля другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        data = {'first_name': 'Hacked'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)