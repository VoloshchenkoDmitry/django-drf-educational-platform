from django.core.management.base import BaseCommand
from django.apps import apps
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Fill database with sample payments'

    def handle(self, *args, **options):
        # Получаем модели через apps чтобы избежать импортов
        User = apps.get_model('users', 'User')
        Course = apps.get_model('materials', 'Course')
        Lesson = apps.get_model('materials', 'Lesson')
        Payment = apps.get_model('users', 'Payment')

        # Получаем или создаем тестовые данные
        users = list(User.objects.all())
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        if not courses and not lessons:
            self.stdout.write(self.style.ERROR('No courses or lessons found. Please create them first.'))
            return

        payment_methods = ['cash', 'transfer']
        amounts = [Decimal('1000.00'), Decimal('1500.00'), Decimal('2000.00'), Decimal('2500.00')]

        payments_created = 0

        for i in range(20):  # Создаем 20 тестовых платежей
            user = random.choice(users)
            payment_date = datetime.now() - timedelta(days=random.randint(0, 30))
            amount = random.choice(amounts)
            payment_method = random.choice(payment_methods)

            # Случайно выбираем курс или урок
            course = None
            lesson = None
            if courses and (not lessons or random.choice([True, False])):
                course = random.choice(courses)
            elif lessons:
                lesson = random.choice(lessons)

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
            self.style.SUCCESS(f'Successfully created {payments_created} payments')
        )