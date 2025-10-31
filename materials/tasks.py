from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription, CourseUpdate


@shared_task
def send_course_update_notification(course_id, update_type, description):
    """
    Отправка уведомлений об обновлении курса подписанным пользователям
    """
    try:
        course = Course.objects.get(id=course_id)
        subscribers = Subscription.objects.filter(course=course).select_related('user')

        subject = f'Обновление курса: {course.title}'

        if update_type == 'course_updated':
            message = f'Курс "{course.title}" был обновлен.\n\n{description}'
        elif update_type == 'lesson_added':
            message = f'В курс "{course.title}" добавлен новый урок.\n\n{description}'
        elif update_type == 'lesson_updated':
            message = f'В курсе "{course.title}" обновлен урок.\n\n{description}'
        else:
            message = f'В курсе "{course.title}" произошли изменения.\n\n{description}'

        recipient_list = [subscriber.user.email for subscriber in subscribers]

        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            return f"Уведомления отправлены {len(recipient_list)} подписчикам курса {course.title}"
        else:
            return "Нет подписчиков для отправки уведомлений"

    except Course.DoesNotExist:
        return f"Курс с id {course_id} не найден"
    except Exception as e:
        return f"Ошибка при отправке уведомлений: {str(e)}"


@shared_task
def send_course_updates_summary():
    """
    Ежедневная сводка об обновлениях курсов
    """
    try:
        yesterday = timezone.now() - timedelta(days=1)

        # Получаем все обновления за последние 24 часа
        recent_updates = CourseUpdate.objects.filter(
            updated_at__gte=yesterday
        ).select_related('course')

        if not recent_updates.exists():
            return "Нет обновлений за последние 24 часа"

        # Группируем обновления по курсам
        updates_by_course = {}
        for update in recent_updates:
            if update.course_id not in updates_by_course:
                updates_by_course[update.course_id] = {
                    'course': update.course,
                    'updates': []
                }
            updates_by_course[update.course_id]['updates'].append(update)

        # Отправляем сводку администраторам
        admin_emails = ['admin@example.com']  # Замените на реальные email админов

        subject = 'Ежедневная сводка об обновлениях курсов'
        message = 'Обновления курсов за последние 24 часа:\n\n'

        for course_data in updates_by_course.values():
            course = course_data['course']
            message += f'Курс: {course.title}\n'
            for update in course_data['updates']:
                message += f'- {update.get_update_type_display()}: {update.description}\n'
            message += '\n'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False,
        )

        return f"Сводка отправлена администраторам. Обновлений: {recent_updates.count()}"

    except Exception as e:
        return f"Ошибка при отправке сводки: {str(e)}"