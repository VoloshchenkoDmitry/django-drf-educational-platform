from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@shared_task
def deactivate_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    """
    try:
        one_month_ago = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более месяца и еще активны
        inactive_users = User.objects.filter(
            last_login__lt=one_month_ago,
            is_active=True
        ).exclude(is_superuser=True)  # Не блокируем суперпользователей

        count_before = inactive_users.count()

        # Деактивируем пользователей
        for user in inactive_users:
            user.is_active = False
            user.save()

            # Отправляем уведомление пользователю
            try:
                send_mail(
                    subject='Ваш аккаунт был деактивирован',
                    message='Ваш аккаунт был автоматически деактивирован из-за длительного отсутствия активности. '
                            'Для восстановления доступа обратитесь в поддержку.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение задачи
                print(f"Ошибка при отправке email пользователю {user.email}: {str(e)}")

        return f"Деактивировано {count_before} неактивных пользователей"

    except Exception as e:
        return f"Ошибка при деактивации пользователей: {str(e)}"


@shared_task
def send_inactivity_warning():
    """
    Отправка предупреждения пользователям, которые не заходили 3 недели
    """
    try:
        three_weeks_ago = timezone.now() - timedelta(days=21)

        # Находим пользователей, которые не заходили 3 недели
        warning_users = User.objects.filter(
            last_login__lt=three_weeks_ago,
            is_active=True
        ).exclude(is_superuser=True)

        for user in warning_users:
            try:
                send_mail(
                    subject='Предупреждение о неактивности аккаунта',
                    message=f'Уважаемый(ая) {user.first_name or "пользователь"}!\n\n'
                            'Мы заметили, что вы не заходили в свой аккаунт более 3 недель. '
                            'Через неделю ваш аккаунт будет автоматически деактивирован для безопасности.\n\n'
                            'Если вы хотите сохранить аккаунт активным, просто войдите в систему.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Ошибка при отправке предупреждения пользователю {user.email}: {str(e)}")

        return f"Предупреждения отправлены {warning_users.count()} пользователям"

    except Exception as e:
        return f"Ошибка при отправке предупреждений: {str(e)}"