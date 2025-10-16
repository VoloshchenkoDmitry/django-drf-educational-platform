from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create moderator group with permissions'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name='moderators')

        if created:
            self.stdout.write(self.style.SUCCESS('Moderators group created'))
        else:
            self.stdout.write(self.style.WARNING('Moderators group already exists'))

        # Получаем разрешения для моделей Course и Lesson
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Разрешения для курсов (все кроме создания и удаления)
        course_permissions = Permission.objects.filter(
            content_type=course_content_type,
            codename__in=['view_course', 'change_course']
        )

        # Разрешения для уроков (все кроме создания и удаления)
        lesson_permissions = Permission.objects.filter(
            content_type=lesson_content_type,
            codename__in=['view_lesson', 'change_lesson']
        )

        # Добавляем разрешения в группу
        moderators_group.permissions.add(*course_permissions)
        moderators_group.permissions.add(*lesson_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f'Added {course_permissions.count() + lesson_permissions.count()} '
                f'permissions to moderators group'
            )
        )