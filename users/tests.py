from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User, Payment
from materials.models import Course, Lesson


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

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

        self.payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=1000.00,
            payment_method='cash'
        )

    def test_user_registration(self):
        """Тест регистрации пользователя"""
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

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        url = reverse('user-register')
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_authenticated(self):
        """Тест получения профиля авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)
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

    def test_user_list_moderator_only(self):
        """Тест получения списка пользователей только модераторами"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

        self.payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=1000.00,
            payment_method='cash'
        )

    def test_payments_list_moderator(self):
        """Тест получения списка платежей модератором"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('payments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payments_list_regular_user(self):
        """Тест получения списка платежей обычным пользователем"""
        self.client.force_authenticate(user=self.user)
        url = reverse('payments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_payments_filtering(self):
        """Тест фильтрации платежей"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('payments-list')

        # Фильтрация по курсу
        response = self.client.get(f'{url}?course={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Фильтрация по способу оплаты
        response = self.client.get(f'{url}?payment_method=cash')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )

        self.token_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')

    def test_token_obtain(self):
        """Тест получения JWT токена"""
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_token_obtain_invalid_credentials(self):
        """Тест получения токена с неверными учетными данными"""
        data = {
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Тест обновления токена"""
        # Сначала получаем токен
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        token_response = self.client.post(self.token_url, data)
        refresh_token = token_response.data['refresh']

        # Обновляем токен
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.token_refresh_url, refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)