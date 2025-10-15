from django.test import TestCase
from django.urls import reverse, resolve
from materials.views import (
    LessonListCreateAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionAPIView
)


class URLTestCase(TestCase):
    def test_lesson_list_url(self):
        """Тест URL списка уроков"""
        url = reverse('lesson-list')
        self.assertEqual(url, '/api/lessons/')
        self.assertEqual(resolve(url).func.view_class, LessonListCreateAPIView)

    def test_lesson_detail_url(self):
        """Тест URL деталей урока"""
        url = reverse('lesson-detail', kwargs={'pk': 1})
        self.assertEqual(url, '/api/lessons/1/')
        self.assertEqual(resolve(url).func.view_class, LessonRetrieveAPIView)

    def test_lesson_update_url(self):
        """Тест URL обновления урока"""
        url = reverse('lesson-update', kwargs={'pk': 1})
        self.assertEqual(url, '/api/lessons/1/update/')
        self.assertEqual(resolve(url).func.view_class, LessonUpdateAPIView)

    def test_lesson_delete_url(self):
        """Тест URL удаления урока"""
        url = reverse('lesson-delete', kwargs={'pk': 1})
        self.assertEqual(url, '/api/lessons/1/delete/')
        self.assertEqual(resolve(url).func.view_class, LessonDestroyAPIView)

    def test_subscription_url(self):
        """Тест URL подписки"""
        url = reverse('subscription')
        self.assertEqual(url, '/api/lessons/subscription/')
        self.assertEqual(resolve(url).func.view_class, SubscriptionAPIView)