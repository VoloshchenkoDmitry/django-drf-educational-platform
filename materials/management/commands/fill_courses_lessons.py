from django.core.management.base import BaseCommand
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Fill database with sample courses and lessons'

    def handle(self, *args, **options):
        # Создаем курсы
        courses_data = [
            {
                'title': 'Python для начинающих',
                'description': 'Полный курс по основам программирования на Python'
            },
            {
                'title': 'Django Framework',
                'description': 'Изучение веб-фреймворка Django для создания современных веб-приложений'
            },
            {
                'title': 'JavaScript и React',
                'description': 'Курс по современному JavaScript и библиотеке React'
            },
            {
                'title': 'Базы данных и SQL',
                'description': 'Основы работы с базами данных и языком запросов SQL'
            }
        ]

        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults=course_data
            )
            courses.append(course)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created course: {course.title}')
                )

        # Создаем уроки для каждого курса
        lessons_data = [
            # Уроки для курса Python
            [
                {'title': 'Введение в Python', 'description': 'Основы языка Python', 'video_link': 'https://example.com/python1'},
                {'title': 'Переменные и типы данных', 'description': 'Работа с переменными', 'video_link': 'https://example.com/python2'},
                {'title': 'Условные операторы', 'description': 'If/else конструкции', 'video_link': 'https://example.com/python3'},
                {'title': 'Циклы', 'description': 'For и while циклы', 'video_link': 'https://example.com/python4'},
            ],
            # Уроки для курса Django
            [
                {'title': 'Введение в Django', 'description': 'Основы фреймворка', 'video_link': 'https://example.com/django1'},
                {'title': 'Модели Django', 'description': 'Создание моделей', 'video_link': 'https://example.com/django2'},
                {'title': 'Представления и URL', 'description': 'Views и URLs', 'video_link': 'https://example.com/django3'},
                {'title': 'Шаблоны', 'description': 'Django Templates', 'video_link': 'https://example.com/django4'},
                {'title': 'Django REST Framework', 'description': 'Создание API', 'video_link': 'https://example.com/django5'},
            ],
            # Уроки для курса JavaScript
            [
                {'title': 'Основы JavaScript', 'description': 'Синтаксис JavaScript', 'video_link': 'https://example.com/js1'},
                {'title': 'DOM манипуляции', 'description': 'Работа с DOM', 'video_link': 'https://example.com/js2'},
                {'title': 'Введение в React', 'description': 'Основы React', 'video_link': 'https://example.com/js3'},
                {'title': 'Компоненты React', 'description': 'Создание компонентов', 'video_link': 'https://example.com/js4'},
            ],
            # Уроки для курса Базы данных
            [
                {'title': 'Введение в БД', 'description': 'Основы баз данных', 'video_link': 'https://example.com/db1'},
                {'title': 'SQL запросы', 'description': 'SELECT, INSERT, UPDATE', 'video_link': 'https://example.com/db2'},
                {'title': 'Нормализация БД', 'description': 'Нормальные формы', 'video_link': 'https://example.com/db3'},
            ]
        ]

        lessons_created = 0
        for i, course in enumerate(courses):
            for lesson_data in lessons_data[i]:
                lesson, created = Lesson.objects.get_or_create(
                    title=lesson_data['title'],
                    course=course,
                    defaults=lesson_data
                )
                if created:
                    lessons_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created lesson: {lesson.title} for course: {course.title}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(courses)} courses and {lessons_created} lessons')
        )