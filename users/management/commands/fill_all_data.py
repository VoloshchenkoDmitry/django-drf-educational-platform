from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Fill database with all sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating courses and lessons...')
        call_command('fill_courses_lessons')

        self.stdout.write('Creating payments...')
        call_command('fill_payments')

        self.stdout.write(
            self.style.SUCCESS('Successfully filled database with all sample data!')
        )