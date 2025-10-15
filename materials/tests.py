from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        """
        Настройка тестовых данных
        """
        # Создаем пользователей
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            first_name='Owner',
            last_name='Test'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123',
            first_name='Moderator',
            last_name='Test'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            price=1000.00,
            owner=self.owner
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_link='https://www.youtube.com/watch?v=test123',
            course=self.course,
            owner=self.owner
        )

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков авторизованным пользователем"""
        print("=== Testing lesson list authenticated ===")
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('lesson-list'))
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков неавторизованным пользователем"""
        print("=== Testing lesson list unauthenticated ===")
        response = self.client.get(reverse('lesson-list'))
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_owner(self):
        """Тест создания урока владельцем"""
        print("=== Testing lesson create owner ===")
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'video_link': 'https://www.youtube.com/watch?v=new123',
            'course': self.course.id
        }
        print(f"Request data: {data}")
        response = self.client.post(reverse('lesson-list'), data)
        print(f"Status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_invalid_video_link(self):
        """Тест создания урока с невалидной ссылкой на видео"""
        print("=== Testing lesson create invalid video ===")
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Invalid Lesson',
            'description': 'Invalid Lesson Description',
            'video_link': 'https://vimeo.com/invalid123',  # Не YouTube ссылка
            'course': self.course.id
        }
        print(f"Request data: {data}")
        response = self.client.post(reverse('lesson-list'), data)
        print(f"Status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if response.status_code == 400:
            self.assertIn('video_link', response.data)

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        print("=== Testing lesson update owner ===")
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated Description'
        }
        print(f"Request data: {data}")
        response = self.client.patch(reverse('lesson-update', kwargs={'pk': self.lesson.pk}), data)
        print(f"Status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_lesson_update_other_user(self):
        """Тест обновления урока другим пользователем"""
        print("=== Testing lesson update other user ===")
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Hacked Lesson'}
        print(f"Request data: {data}")
        response = self.client.patch(reverse('lesson-update', kwargs={'pk': self.lesson.pk}), data)
        print(f"Status: {response.status_code}")
        print(f"Response data: {response.data}")
        # Должен быть 404, так как урок не принадлежит пользователю
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        print("=== Testing lesson delete owner ===")
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(reverse('lesson-delete', kwargs={'pk': self.lesson.pk}))
        print(f"Status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_other_user(self):
        """Тест удаления урока другим пользователем"""
        print("=== Testing lesson delete other user ===")
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(reverse('lesson-delete', kwargs={'pk': self.lesson.pk}))
        print(f"Status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Lesson.objects.count(), 1)