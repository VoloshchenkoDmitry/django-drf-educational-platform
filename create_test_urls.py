from django.test import TestCase
from django.urls import reverse, resolve
from materials.views import LessonListCreateAPIView


class URLTestCase(TestCase):
    def test_lesson_urls(self):
        """Тест что URLs уроков работают"""
        # Проверяем разрешение URL
        url = reverse('lesson-list')
        self.assertEqual(resolve(url).func.view_class, LessonListCreateAPIView)

        # Проверяем другие URLs
        self.assertEqual(reverse('subscription'), '/api/lessons/subscription/')
        self.assertEqual(reverse('course-list'), '/api/courses/')