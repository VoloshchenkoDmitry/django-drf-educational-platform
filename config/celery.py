import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Использование строки настроек для конфигурации Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из приложений
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'deactivate-inactive-users': {
        'task': 'users.tasks.deactivate_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # Ежедневно в полночь
    },
    'send-inactivity-warnings': {
        'task': 'users.tasks.send_inactivity_warning',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Каждый понедельник в 9:00
    },
    'send-course-updates-summary': {
        'task': 'materials.tasks.send_course_updates_summary',
        'schedule': crontab(hour=8, minute=0),  # Ежедневно в 8:00
    },
}

app.conf.timezone = 'Europe/Moscow'