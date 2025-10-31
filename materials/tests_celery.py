from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from .models import Course, Subscription, CourseUpdate
from .tasks import send_course_update_notification, send_course_updates_summary
from users.models import User


class CeleryTasksTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            course=self.course
        )

    @patch('materials.tasks.send_mail')
    def test_send_course_update_notification(self, mock_send_mail):
        """Тест отправки уведомления об обновлении курса"""
        mock_send_mail.return_value = 1

        result = send_course_update_notification(
            self.course.id,
            'course_updated',
            'Test update description'
        )

        mock_send_mail.assert_called_once()
        self.assertIn('Уведомления отправлены', result)

    @patch('materials.tasks.send_mail')
    def test_send_course_updates_summary(self, mock_send_mail):
        """Тест отправки сводки об обновлениях"""
        # Создаем тестовое обновление
        CourseUpdate.objects.create(
            course=self.course,
            update_type='course_updated',
            description='Test update'
        )

        mock_send_mail.return_value = 1

        result = send_course_updates_summary()

        mock_send_mail.assert_called_once()
        self.assertIn('Сводка отправлена', result)