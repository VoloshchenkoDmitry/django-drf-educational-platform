from django.core.management.base import BaseCommand
from users.models import User, Payment
from materials.models import Course, Lesson
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Fill database with sample payments'

    def handle(self, *args, **options):
        # Получаем пользователей
        users = list(User.objects.all())

        # Если нет пользователей, создаем тестового
        if not users:
            user = User.objects.create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User',
                phone='+79991234567',
                city='Moscow'
            )
            users = [user]
            self.stdout.write(self.style.WARNING('Created test user: test@example.com'))

        # Получаем курсы и уроки
        courses_list = list(Course.objects.all())
        lessons_list = list(Lesson.objects.all())

        # Если нет курсов и уроков, создаем минимальный набор
        if not courses_list and not lessons_list:
            self.stdout.write(self.style.WARNING('No courses or lessons found. Creating sample data...'))

            # Создаем базовый курс
            basic_course = Course.objects.create(
                title='Основы программирования',
                description='Вводный курс по программированию'
            )
            courses_list = [basic_course]

            # Создаем базовый урок
            basic_lesson = Lesson.objects.create(
                title='Первые шаги в программировании',
                description='Введение в программирование',
                video_link='https://example.com/intro',
                course=basic_course
            )
            lessons_list = [basic_lesson]

            self.stdout.write(self.style.WARNING('Created sample course and lesson'))

        payment_methods = ['cash', 'transfer']
        amounts = [Decimal('1000.00'), Decimal('1500.00'), Decimal('2000.00'), Decimal('2500.00'), Decimal('500.00')]

        payments_created = 0

        # Создаем 15-20 тестовых платежей
        for i in range(random.randint(15, 20)):
            user = random.choice(users)
            payment_date = datetime.now() - timedelta(days=random.randint(0, 60))
            amount = random.choice(amounts)
            payment_method = random.choice(payment_methods)

            # Случайно выбираем курс или урок
            course = None
            lesson = None

            if courses_list and lessons_list:
                # 70% вероятность оплаты курса, 30% - урока
                if random.random() < 0.7:
                    course = random.choice(courses_list)
                else:
                    lesson = random.choice(lessons_list)
            elif courses_list:
                course = random.choice(courses_list)
            elif lessons_list:
                lesson = random.choice(lessons_list)

            try:
                payment = Payment.objects.create(
                    user=user,
                    payment_date=payment_date,
                    course=course,
                    lesson=lesson,
                    amount=amount,
                    payment_method=payment_method
                )
                payments_created += 1

                self.stdout.write(
                    self.style.SUCCESS(f'Created payment #{payments_created}: {user.email} - {amount} {payment_method}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating payment: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {payments_created} payments')
        )