from django.core.management.base import BaseCommand
from users.models import User
from materials.models import Course, Lesson
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test users, courses and lessons'

    def handle(self, *args, **options):
        # Создаем тестовых пользователей
        users_data = [
            {'email': 'user1@test.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'user2@test.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'email': 'user3@test.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
            {'email': 'moderator@test.com', 'first_name': 'Alice', 'last_name': 'Moderator'},
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))
            else:
                users.append(user)
                self.stdout.write(self.style.WARNING(f'User already exists: {user.email}'))

        # Создаем тестовые курсы
        courses_data = [
            {
                'title': 'Python Programming',
                'description': 'Learn Python from scratch',
                'price': Decimal('1500.00')
            },
            {
                'title': 'Django Web Development',
                'description': 'Build web applications with Django',
                'price': Decimal('2000.00')
            },
            {
                'title': 'React Frontend',
                'description': 'Modern frontend development with React',
                'price': Decimal('1800.00')
            },
        ]

        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'description': course_data['description'],
                    'price': course_data['price'],
                    'owner': users[0]  # Первый пользователь - владелец
                }
            )
            if created:
                courses.append(course)
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
            else:
                courses.append(course)
                self.stdout.write(self.style.WARNING(f'Course already exists: {course.title}'))

        # Создаем тестовые уроки
        lessons_data = [
            {
                'title': 'Python Basics',
                'description': 'Introduction to Python syntax',
                'video_link': 'https://www.youtube.com/watch?v=abc123',
                'course': courses[0]
            },
            {
                'title': 'Python Functions',
                'description': 'Learn about functions in Python',
                'video_link': 'https://www.youtube.com/watch?v=def456',
                'course': courses[0]
            },
            {
                'title': 'Django Models',
                'description': 'Working with Django ORM',
                'video_link': 'https://www.youtube.com/watch?v=ghi789',
                'course': courses[1]
            },
            {
                'title': 'Django Views',
                'description': 'Creating views in Django',
                'video_link': 'https://www.youtube.com/watch?v=jkl012',
                'course': courses[1]
            },
            {
                'title': 'React Components',
                'description': 'Building React components',
                'video_link': 'https://www.youtube.com/watch?v=mno345',
                'course': courses[2]
            },
        ]

        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                title=lesson_data['title'],
                course=lesson_data['course'],
                defaults={
                    'description': lesson_data['description'],
                    'video_link': lesson_data['video_link'],
                    'owner': users[0]  # Первый пользователь - владелец
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created lesson: {lesson.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Lesson already exists: {lesson.title}'))

        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))