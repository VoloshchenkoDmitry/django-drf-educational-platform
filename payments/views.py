from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Payment, Subscription
from .serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    PaymentHistorySerializer
)
from .services import create_payment_flow, get_stripe_session_status, update_payment_status
from materials.models import Course
from users.permissions import IsModerator
from config.stripe_config import STRIPE_API_KEY


class PaymentListAPIView(generics.ListAPIView):
    """
    Получение списка платежей (только для модераторов)
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsModerator]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method', 'status']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']

    def get_queryset(self):
        return Payment.objects.select_related('user', 'course', 'lesson')


class PaymentCreateAPIView(APIView):
    """
    Создание платежа для курса через Stripe
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создать платеж для курса",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса')
            },
            required=['course_id']
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'payment_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'course': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            500: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        # Проверяем настройку Stripe
        if not STRIPE_API_KEY or STRIPE_API_KEY.startswith('sk_test_default'):
            return Response(
                {"error": "Stripe не настроен. Обратитесь к администратору."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        # Проверяем, не оплачен ли уже курс
        existing_paid_payment = Payment.objects.filter(
            user=user,
            course=course,
            status='paid'
        ).exists()

        if existing_paid_payment:
            return Response(
                {"error": "Курс уже оплачен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Получаем базовый URL для callback
            base_url = request.build_absolute_uri('/')[:-1]

            # Создаем платеж
            payment = create_payment_flow(course, user, base_url)

            return Response({
                "id": payment.id,
                "payment_url": payment.payment_url,
                "amount": float(payment.amount),
                "course": course.title,
                "status": payment.status,
                "message": "Ссылка для оплаты создана"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentSuccessAPIView(APIView):
    """
    Обработка успешной оплаты
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Эндпоинт для перенаправления после успешной оплаты",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )}
    )
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id:
            try:
                payment = update_payment_status(session_id)
                return Response({
                    "message": "Оплата прошла успешно! Спасибо за покупку.",
                    "course": payment.course.title if payment.course else None,
                    "amount": float(payment.amount)
                })
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response({"message": "Оплата прошла успешно! Спасибо за покупку."})


class PaymentCancelAPIView(APIView):
    """
    Обработка отмены оплаты
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Эндпоинт для перенаправления после отмены оплаты",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )}
    )
    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата отменена. Вы можете попробовать снова."})


class PaymentStatusAPIView(APIView):
    """
    Проверка статуса платежа
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Проверить статус платежа",
        manual_parameters=[
            openapi.Parameter(
                'payment_id',
                openapi.IN_QUERY,
                description="ID платежа в системе",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'session_id',
                openapi.IN_QUERY,
                description="ID сессии в Stripe",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'paid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER)
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('payment_id')
        session_id = request.GET.get('session_id')

        if not payment_id and not session_id:
            return Response(
                {"error": "Необходимо указать payment_id или session_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if payment_id:
                payment = get_object_or_404(Payment, id=payment_id, user=request.user)
                session_id = payment.stripe_session_id
            else:
                payment = get_object_or_404(Payment, stripe_session_id=session_id, user=request.user)

            # Получаем статус из Stripe и обновляем
            payment = update_payment_status(session_id)

            return Response({
                "payment_id": payment.id,
                "status": payment.status,
                "paid": payment.status == 'paid',
                "amount": float(payment.amount),
                "course": payment.course.title if payment.course else None
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return SubscriptionCreateSerializer
        return SubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Управление подпиской на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса')
            }
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
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Включение/выключение подписки на курс
        """
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course).first()

        if subscription:
            subscription.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'

        return Response({"message": message})


class UserPaymentHistoryAPIView(generics.ListAPIView):
    """
    История платежей текущего пользователя
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('course', 'lesson')