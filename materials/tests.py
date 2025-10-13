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

        # URL для тестов
        self.lessons_list_url = reverse('lesson-list-create')
        self.lesson_detail_url = reverse('lesson-retrieve', kwargs={'pk': self.lesson.pk})
        self.lesson_update_url = reverse('lesson-update', kwargs={'pk': self.lesson.pk})
        self.lesson_delete_url = reverse('lesson-delete', kwargs={'pk': self.lesson.pk})

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков авторизованным пользователем"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков неавторизованным пользователем"""
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_owner(self):
        """Тест создания урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'video_link': 'https://www.youtube.com/watch?v=new123',
            'course': self.course.id
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_invalid_video_link(self):
        """Тест создания урока с невалидной ссылкой на видео"""
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Invalid Lesson',
            'description': 'Invalid Lesson Description',
            'video_link': 'https://vimeo.com/invalid123',
            'course': self.course.id
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated Description'
        }
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_lesson_update_other_user(self):
        """Тест обновления урока другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Hacked Lesson'}
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_other_user(self):
        """Тест удаления урока другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Lesson.objects.count(), 1)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        """
        Настройка тестовых данных для подписок
        """
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course for Subscription',
            description='Test Description',
            owner=self.user
        )

        self.subscription_url = reverse('subscription')

    def test_subscription_create(self):
        """Тест создания подписки"""
        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertIn('добавлена', response.data['message'])

    def test_subscription_delete(self):
        """Тест удаления подписки"""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 0)
        self.assertIn('удалена', response.data['message'])

    def test_subscription_without_course_id(self):
        """Тест подписки без course_id"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscription_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('course_id', response.data['error'])

    def test_subscription_unauthenticated(self):
        """Тест подписки неавторизованным пользователем"""
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

        # Создаем несколько уроков для курса
        Lesson.objects.create(
            title='Lesson 1',
            description='Description 1',
            course=self.course,
            owner=self.user
        )
        Lesson.objects.create(
            title='Lesson 2',
            description='Description 2',
            course=self.course,
            owner=self.user
        )

    def test_course_serializer_lessons_count(self):
        """Тест подсчета количества уроков в сериализаторе курса"""
        from .serializers import CourseSerializer

        serializer = CourseSerializer(self.course)
        self.assertEqual(serializer.data['lessons_count'], 2)

    def test_course_serializer_is_subscribed(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        from .serializers import CourseSerializer
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user

        serializer = CourseSerializer(
            self.course,
            context={'request': request}
        )

        # Изначально пользователь не подписан
        self.assertFalse(serializer.data['is_subscribed'])

        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        serializer = CourseSerializer(
            self.course,
            context={'request': request}
        )
        self.assertTrue(serializer.data['is_subscribed'])


class CourseViewSetTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.owner
        )

        self.courses_list_url = reverse('course-list')
        self.course_detail_url = reverse('course-detail', kwargs={'pk': self.course.pk})

    def test_course_list_authenticated(self):
        """Тест получения списка курсов авторизованным пользователем"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.courses_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_create_authenticated(self):
        """Тест создания курса авторизованным пользователем"""
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'New Course',
            'description': 'New Course Description'
        }
        response = self.client.post(self.courses_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_update_owner(self):
        """Тест обновления курса владельцем"""
        self.client.force_authenticate(user=self.owner)
        data = {'title': 'Updated Course'}
        response = self.client.patch(self.course_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')

    def test_course_update_other_user(self):
        """Тест обновления курса другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Hacked Course'}
        response = self.client.patch(self.course_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)