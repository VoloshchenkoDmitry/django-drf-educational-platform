from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Course, Lesson, Subscription, CourseUpdate
from .serializers import CourseSerializer, LessonSerializer
from .permissions import CoursePermission, LessonPermission
from .paginators import LessonPaginator, CoursePaginator
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [CoursePermission]
    pagination_class = CoursePaginator

    @swagger_auto_schema(
        operation_description="Получить список курсов",
        responses={200: CourseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получить детальную информацию о курсе",
        responses={200: CourseSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый курс",
        request_body=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновить курс",
        request_body=CourseSerializer,
        responses={200: CourseSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()

        # Проверяем, было ли обновление более 4 часов назад
        four_hours_ago = timezone.now() - timedelta(hours=4)
        last_update = CourseUpdate.objects.filter(
            course=instance,
            update_type='course_updated'
        ).order_by('-updated_at').first()

        should_send_notification = True
        if last_update and last_update.updated_at > four_hours_ago:
            should_send_notification = False

        if should_send_notification:
            # Создаем запись об обновлении
            CourseUpdate.objects.create(
                course=instance,
                update_type='course_updated',
                description=f'Курс "{instance.title}" был обновлен'
            )

            # Отправляем уведомления асинхронно
            send_course_update_notification.delay(
                course_id=instance.id,
                update_type='course_updated',
                description=f'Курс "{instance.title}" был обновлен'
            )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [LessonPermission]
    pagination_class = LessonPaginator

    @swagger_auto_schema(
        operation_description="Получить список уроков с пагинацией",
        responses={200: LessonSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый урок",
        request_body=LessonSerializer,
        responses={201: LessonSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        lesson = serializer.save(owner=self.request.user)

        # Отправляем уведомление о новом уроке
        CourseUpdate.objects.create(
            course=lesson.course,
            update_type='lesson_added',
            description=f'Добавлен новый урок: "{lesson.title}"'
        )

        send_course_update_notification.delay(
            course_id=lesson.course.id,
            update_type='lesson_added',
            description=f'Добавлен новый урок: "{lesson.title}"'
        )

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [LessonPermission]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [LessonPermission]

    def perform_update(self, serializer):
        lesson = serializer.save()

        # Проверяем, было ли обновление курса более 4 часов назад
        four_hours_ago = timezone.now() - timedelta(hours=4)
        last_update = CourseUpdate.objects.filter(
            course=lesson.course,
            update_type='lesson_updated'
        ).order_by('-updated_at').first()

        should_send_notification = True
        if last_update and last_update.updated_at > four_hours_ago:
            should_send_notification = False

        if should_send_notification:
            # Создаем запись об обновлении
            CourseUpdate.objects.create(
                course=lesson.course,
                update_type='lesson_updated',
                description=f'Обновлен урок: "{lesson.title}"'
            )

            # Отправляем уведомления асинхронно
            send_course_update_notification.delay(
                course_id=lesson.course.id,
                update_type='lesson_updated',
                description=f'Обновлен урок: "{lesson.title}"'
            )

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [LessonPermission]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionAPIView(APIView):
    """
    APIView для управления подписками на курсы
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Управление подпиской на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса')
            },
            required=['course_id']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course_item)

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'

        return Response({"message": message})