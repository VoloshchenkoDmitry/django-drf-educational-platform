from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Payment
from users.models import User
from materials.models import Course


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

        # Добавляем пользователя в группу модераторов
        from django.contrib.auth.models import Group
        moderators_group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(moderators_group)

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
        # Обычный пользователь не должен иметь доступ
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)