from django.core.management.base import BaseCommand
from materials.models import Course, Lesson
from users.models import User
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create test data for all models'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderators_group, _ = Group.objects.get_or_create(name='moderators')

        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Создаем модератора
        moderator, created = User.objects.get_or_create(
            email='moderator@example.com',
            defaults={
                'first_name': 'Moderator',
                'last_name': 'User',
            }
        )
        if created:
            moderator.set_password('testpass123')
            moderator.save()
            moderator.groups.add(moderators_group)
            self.stdout.write(self.style.SUCCESS('Created moderator user'))

        courses_data = [
            {
                'title': 'Python для начинающих',
                'description': 'Основы программирования на Python',
                'price': 5000.00,
            },
            {
                'title': 'Django Professional',
                'description': 'Продвинутый курс по Django',
                'price': 15000.00,
            },
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'description': course_data['description'],
                    'price': course_data['price'],
                    'owner': user
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created course: {course.title} - {course.price} руб')
                )

                lessons_data = [
                    {
                        'title': f'Введение в {course.title}',
                        'description': f'Первое занятие',
                        'video_link': 'https://www.youtube.com/watch?v=test1',
                    },
                    {
                        'title': f'Практика {course.title}',
                        'description': f'Практическое занятие',
                        'video_link': 'https://youtu.be/test2',
                    }
                ]

                for lesson_data in lessons_data:
                    lesson = Lesson.objects.create(
                        title=lesson_data['title'],
                        description=lesson_data['description'],
                        video_link=lesson_data['video_link'],
                        course=course,
                        owner=user
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'  - Created lesson: {lesson.title}')
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully created test data')
        )