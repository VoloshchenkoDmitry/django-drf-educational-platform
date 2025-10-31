from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from .models import User
from .tasks import deactivate_inactive_users, send_inactivity_warning


class UserCeleryTasksTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='inactive@test.com',
            password='testpass123',
            last_login=timezone.now() - timedelta(days=35)
        )

    @patch('users.tasks.send_mail')
    def test_deactivate_inactive_users(self, mock_send_mail):
        """Тест деактивации неактивных пользователей"""
        mock_send_mail.return_value = 1

        result = deactivate_inactive_users()

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertIn('Деактивировано', result)

    @patch('users.tasks.send_mail')
    def test_send_inactivity_warning(self, mock_send_mail):
        """Тест отправки предупреждений о неактивности"""
        warning_user = User.objects.create_user(
            email='warning@test.com',
            password='testpass123',
            last_login=timezone.now() - timedelta(days=25)
        )

        mock_send_mail.return_value = 1

        result = send_inactivity_warning()

        mock_send_mail.assert_called()
        self.assertIn('Предупреждения отправлены', result)