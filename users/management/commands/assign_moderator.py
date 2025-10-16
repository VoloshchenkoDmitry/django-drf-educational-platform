from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import User


class Command(BaseCommand):
    help = 'Assign moderator role to a user'

    def handle(self, *args, **options):
        try:
            # Находим группу модераторов
            moderators_group = Group.objects.get(name='moderators')

            # Находим пользователя
            user = User.objects.get(email='moderator@test.com')

            # Добавляем пользователя в группу
            user.groups.add(moderators_group)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'User {user.email} added to moderators group')
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('User moderator@test.com not found. Run create_test_data first.')
            )
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Moderators group not found. Run create_groups first.')
            )