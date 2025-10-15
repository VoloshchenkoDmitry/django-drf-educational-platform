from .settings import *

# Специальные настройки для тестов
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1', '*']
DEBUG = True

# Отключаем некоторые системные проверки для тестов
SILENCED_SYSTEM_CHECKS = [
    'security.W019',  # ALLOWED_HOSTS
]

# Используем тестовую базу данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Используем in-memory базу для тестов
    }
}