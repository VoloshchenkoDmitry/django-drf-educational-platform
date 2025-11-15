# Learning Management System (LMS)

Полнофункциональная система управления обучением на основе Django REST Framework с интеграцией платежей, email уведомлений и фоновыми задачами.

## 📋 Оглавление

- [Функциональность]
- [Технологический стек]
- [Быстрый старт]
- [Детальная установка]
- [Настройка окружения]
- [API Endpoints]
- [Документация API]
- [Тестирование]
- [Управление сервисами]
- [Разработка]
- [Модели данных]
- [Решение проблем]

## 🚀 Функциональность

### Основные модули
- **Аутентификация** - JWT токены, регистрация, профили пользователей
- **Управление контентом** - Курсы, уроки, превью, описания
- **Платежная система** - Интеграция со Stripe, история платежей
- **Система подписок** - Уведомления об обновлениях курсов
- **Роли и права** - Модераторы, владельцы контента, обычные пользователи
- **Email рассылки** - Асинхронные уведомления через Celery

### Безопасность и валидация
- Валидация YouTube ссылок в уроках
- Права доступа на уровне объектов
- Автоматическая блокировка неактивных пользователей
- Защита от массовой рассылки уведомлений

### Фоновые задачи
- Отправка email уведомлений
- Управление подписками
- Периодическая чистка неактивных пользователей
- Ежедневные отчеты

## 🛠 Технологический стек

### Backend
- **Python 3.11** - Основной язык программирования
- **Django 4.2** - Веб-фреймворк
- **Django REST Framework** - API фреймворк
- **Django REST Simple JWT** - Аутентификация
- **Celery** - Асинхронные задачи
- **Redis** - Брокер сообщений и кэш
- **PostgreSQL** - База данных
- **Stripe** - Платежная система

### Дополнительные компоненты
- **DRF Yasg** - Документация API
- **Django Filter** - Фильтрация данных
- **Pillow** - Работа с изображениями
- **WhiteNoise** - Статические файлы
- **Python Dotenv** - Переменные окружения

### Инфраструктура
- **Docker** - Контейнеризация
- **Docker Compose** - Оркестрация контейнеров
- **Gunicorn** - WSGI сервер (production)

## ⚡ Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <URL-репозитория>
cd lms-project

### 2. Базовая настройка
# Копируем шаблон окружения
cp .env.example .env

# Запускаем все сервисы
docker-compose up --build

### 3. Первоначальная настройка
bash
# В новом терминале применяем миграции
docker-compose exec backend python manage.py migrate

# Создаем суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Создаем группы модераторов
docker-compose exec backend python manage.py create_groups

###4. Проверка работоспособности
Откройте в браузере:

API: http://localhost:8000/api/

Админка: http://localhost:8000/admin/

Документация: http://localhost:8000/swagger/

 🔧 Детальная установка
Шаг 1: Подготовка системы
Убедитесь, что установлены:
Docker 20.10+
Docker Compose 2.0+
Проверьте установку:

docker --version
docker-compose --version

Шаг 2: Настройка проекта
# Клонирование
git clone <repository-url>
cd lms-project

# Создание файла окружения
cp .env.example .env

Шаг 3: Конфигурация окружения
Отредактируйте файл .env:
# Django Settings
DEBUG=True
SECRET_KEY=your-very-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=lms_db
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=strong_password_123
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Email Settings (опционально)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your.email@gmail.com

# Stripe Settings (опционально)
STRIPE_API_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Celery Settings
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

Шаг 4: Запуск контейнеров
# Полный запуск с сборкой образов
docker-compose up --build

# Или запуск в фоновом режиме
docker-compose up -d --build

Шаг 5: Мониторинг запуска
# Проверка статуса сервисов
docker-compose ps

# Просмотр логов в реальном времени
docker-compose logs -f

# Проверка здоровья сервисов
docker-compose exec db pg_isready
docker-compose exec redis redis-cli ping
curl http://localhost:8000/api/

Шаг 6: Инициализация базы данных
# Применение миграций
docker-compose exec backend python manage.py migrate

# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Создание групп модераторов
docker-compose exec backend python manage.py create_groups

# Создание тестовых данных (опционально)
docker-compose exec backend python manage.py fill_payments

# Сбор статических файлов
docker-compose exec backend python manage.py collectstatic --noinput

⚙️ Настройка окружения
Обязательные переменные
SECRET_KEY=              # Секретный ключ Django
POSTGRES_DB=            # Имя базы данных
POSTGRES_USER=          # Пользователь БД
POSTGRES_PASSWORD=      # Пароль БД
Опциональные переменные для расширенной функциональности

# Email для уведомлений
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Stripe для платежей
STRIPE_API_KEY=
STRIPE_PUBLISHABLE_KEY=
Настройка Email (Gmail пример)
Включите 2FA в аккаунте Google

Создайте "Пароль приложения"

Укажите в .env:

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=your_16_digit_app_password
Настройка Stripe
Зарегистрируйтесь на https://stripe.com

Получите тестовые ключи из панели управления

Укажите в .env:
STRIPE_API_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

📡 API Endpoints
Аутентификация
Метод	Endpoint	Описание	Тело запроса
POST	/api/users/register/	Регистрация	email, password, password_confirm, first_name, last_name
POST	/api/token/	Получение JWT	email, password
POST	/api/token/refresh/	Обновление токена	refresh

Пользователи
Метод	Endpoint	Права доступа
GET	/api/users/	Только модераторы
GET	/api/users/{id}/	Авторизованные пользователи
PUT/PATCH	/api/users/{id}/	Только владелец профиля
GET	/api/users/{id}/profile/	Авторизованные пользователи

Курсы
Метод	Endpoint	Описание	Права
GET	/api/courses/	Список курсов	Все
POST	/api/courses/	Создание курса	Авторизованные
GET	/api/courses/{id}/	Детали курса	Все
PUT/PATCH	/api/courses/{id}/	Обновление	Владелец/Модератор
DELETE	/api/courses/{id}/	Удаление	Только владелец

Уроки
Метод	Endpoint	Описание
GET	/api/lessons/	Список уроков с пагинацией
POST	/api/lessons/	Создание урока
GET	/api/lessons/{id}/	Детали урока
PUT/PATCH	/api/lessons/{id}/update/	Обновление урока
DELETE	/api/lessons/{id}/delete/	Удаление урока

Подписки
Метод	Endpoint	Описание	Тело запроса
POST	/api/lessons/subscription/	Вкл/Выкл подписку	{"course_id": 1}
Платежи
Метод	Endpoint	Описание	Тело запроса
POST	/api/lessons/payments/create/	Создать платеж	{"course_id": 1}
GET	/api/lessons/payments/status/	Статус платежа	Query: payment_id или session_id
GET	/api/payments/	Список платежей	Только модераторы

📚 Документация API
Автоматическая документация
После запуска проекта доступно:

Swagger UI: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/

JSON Schema: http://localhost:8000/swagger.json

Примеры запросов
Регистрация пользователя
bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
Создание курса
bash
curl -X POST http://localhost:8000/api/courses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Django для начинающих",
    "description": "Полный курс по Django",
    "price": 1500.00
  }'
Управление подпиской
curl -X POST http://localhost:8000/api/lessons/subscription/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"course_id": 1}'

🧪 Тестирование
Запуск тестов
# Все тесты
docker-compose exec backend python manage.py test

# Конкретное приложение
docker-compose exec backend python manage.py test users
docker-compose exec backend python manage.py test materials
docker-compose exec backend python manage.py test payments

# С покрытием кода
docker-compose exec backend coverage run manage.py test
docker-compose exec backend coverage report
docker-compose exec backend coverage html

# Запуск конкретного теста
docker-compose exec backend python manage.py test materials.tests.LessonTestCase
Тестирование API через curl
Получение токена
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "adminpassword"}'

Создание урока
curl -X POST http://localhost:8000/api/lessons/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Введение в Django",
    "description": "Основы Django фреймворка",
    "video_link": "https://www.youtube.com/watch?v=example",
    "course": 1
  }'
  
Тестирование платежей
# Создание платежа
curl -X POST http://localhost:8000/api/lessons/payments/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"course_id": 1}'

🔄 Управление сервисами
Основные команды Docker Compose

Запуск и остановка

# Запуск всех сервисов
docker-compose up
docker-compose up -d  # Фоновый режим

# Остановка всех сервисов
docker-compose down
docker-compose down -v  # С удалением volumes

# Перезапуск
docker-compose restart
docker-compose restart backend  # Конкретный сервис

# Просмотр статуса
docker-compose ps
docker-compose images

Логи и мониторинг

# Просмотр логов
docker-compose logs
docker-compose logs -f  # Реальный времени
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f celery-beat

# Мониторинг ресурсов
docker-compose stats
docker system df  # Использование диска
Выполнение команд
# Django management commands
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# База данных
docker-compose exec db psql -U lms_user -d lms_db

# Redis
docker-compose exec redis redis-cli
docker-compose exec redis redis-cli ping
Управление Celery

Мониторинг задач
# Статус Celery
docker-compose exec celery celery -A config status

# Активные задачи
docker-compose exec celery celery -A config inspect active

# Запланированные задачи
docker-compose exec celery celery -A config inspect scheduled

# Статистика
docker-compose exec celery celery -A config inspect stats
Управление очередью

# Очистка очереди
docker-compose exec celery celery -A config purge

# Просмотр зарегистрированных задач
docker-compose exec celery celery -A config inspect registered

# Принудительный запуск задачи
docker-compose exec backend python -c "from users.tasks import deactivate_inactive_users; deactivate_inactive_users.delay()"

Резервное копирование

# Дамп базы данных
docker-compose exec db pg_dump -U lms_user lms_db > backup_$(date +%Y%m%d).sql

# Восстановление из дампа
docker-compose exec -T db psql -U lms_user lms_db < backup.sql

# Копирование медиа файлов
docker cp lms_backend:/app/media ./media_backup/

🛠 Разработка
Локальная разработка без Docker

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных (SQLite для разработки)
python manage.py migrate
python manage.py createsuperuser
python manage.py create_groups

# Запуск сервисов
python manage.py runserver  # Django
redis-server                # Redis
celery -A config worker --loglevel=info  # Celery worker
celery -A config beat --loglevel=info    # Celery beat

Структура проекта
text
lms-project/
├── config/                 # Настройки Django
│   ├── settings.py        # Основные настройки
│   ├── urls.py           # URL конфигурация
│   ├── celery.py         # Конфигурация Celery
│   └── wsgi.py           # WSGI конфигурация
├── users/                 # Приложение пользователей
│   ├── models.py         # Модель User, Payment
│   ├── serializers.py    # Сериализаторы
│   ├── views.py          # ViewSets и API views
│   ├── permissions.py    # Кастомные permissions
│   └── tasks.py          # Celery задачи
├── materials/            # Приложение курсов и уроков
│   ├── models.py         # Course, Lesson, Subscription
│   ├── serializers.py    # Сериализаторы
│   ├── views.py          # ViewSets
│   ├── permissions.py    # Права доступа
│   ├── tasks.py          # Email уведомления
│   └── validators.py     # Валидаторы YouTube ссылок
├── payments/             # Приложение платежей
│   ├── models.py         # Модель Payment
│   ├── serializers.py    # Сериализаторы платежей
│   ├── views.py          # Views для платежей
│   └── services.py       # Интеграция со Stripe
├── docker-compose.yaml   # Конфигурация Docker Compose
├── Dockerfile           # Образ для бэкенда
├── requirements.txt     # Зависимости Python
├── .env.example        # Шаблон переменных окружения
└── manage.py           # Django management script

Создание миграций
# Создание миграций после изменения моделей
docker-compose exec backend python manage.py makemigrations

# Применение миграций
docker-compose exec backend python manage.py migrate

# Создание пустых миграций
docker-compose exec backend python manage.py makemigrations --empty app_name

# Откат миграций
docker-compose exec backend python manage.py migrate app_name previous_migration

Кастомные management commands

# Создание групп модераторов
docker-compose exec backend python manage.py create_groups

# Заполнение тестовыми платежами
docker-compose exec backend python manage.py fill_payments

# Проверка системы
docker-compose exec backend python manage.py check

🗄 Модели данных
Пользователи (users)

User - Кастомная модель пользователя с email аутентификацией
Payment - История платежей пользователей

Материалы (materials)
Course - Курсы с уроками, ценой и владельцем
Lesson - Уроки с видео и привязкой к курсу
Subscription - Подписки пользователей на курсы
CourseUpdate - История обновлений курсов

Основные связи

User 1:N Course (owner)

User 1:N Lesson (owner)

User 1:N Payment

User N:M Course (через Subscription)

Course 1:N Lesson

Course 1:N Subscription

❗ Решение проблем

Общие проблемы
1.Порт уже используется

# Найдите процесс использующий порт
sudo lsof -i :8000
# Или
netstat -tulpn | grep :8000

# Освободите порт или измените в docker-compose.yaml

2.Ошибки базы данных

# Сброс базы данных
docker-compose down -v
docker-compose up -d db
docker-compose exec backend python manage.py migrate

# Проверка подключения к БД
docker-compose exec backend python manage.py dbshell

3.Проблемы с Docker

# Очистка Docker
docker system prune
docker volume prune
docker image prune

# Перезапуск Docker домена
sudo systemctl restart docker

# Проверка свободного места
docker system df

4.Проблемы с Celery
Задачи не выполняются

# Проверьте подключение к Redis
docker-compose exec redis redis-cli ping

# Перезапустите Celery
docker-compose restart celery celery-beat

# Проверьте логи
docker-compose logs -f celery

# Проверьте зарегистрированные задачи
docker-compose exec celery celery -A config inspect registered

5.Очередь задач переполнена

# Очистка очереди
docker-compose exec celery celery -A config purge

# Принудительный запуск worker
docker-compose exec celery celery -A config worker --loglevel=debug

6.Проблемы с Email
Ошибки отправки email

# Проверьте настройки в .env
docker-compose exec backend python -c "
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
"

# Для Gmail используйте "Пароль приложения"
# Убедитесь что EMAIL_USE_TLS=True

7.Проблемы с Stripe
Ошибки платежей

# Проверьте Stripe ключи
docker-compose exec backend python -c "
import stripe
stripe.api_key = 'your_key'
print(stripe.Account.retrieve())
"

# Используйте тестовые карты Stripe:
# Номер: 4242 4242 4242 4242
# Дата: любая будущая
# CVC: любой 3 цифры

###Логи и отладка

8.Просмотр логов

# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs backend
docker-compose logs celery

# Логи в реальном времени
docker-compose logs -f

# Логи за определенный период
docker-compose logs --since 1h

# Войти в контейнер
docker-compose exec backend bash

# Запустить Django shell
docker-compose exec backend python manage.py shell

# Проверить настройки
docker-compose exec backend python manage.py check
