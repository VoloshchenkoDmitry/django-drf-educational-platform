from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.permissions import IsModerator
from .models import Payment
from .serializers import PaymentSerializer
from .services import create_payment_flow, get_stripe_session_status
from materials.models import Course


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsModerator]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']


class PaymentCreateAPIView(views.APIView):
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

        course = get_object_or_404(Course, id=course_id)

        # Проверяем, не оплачен ли уже курс
        existing_payment = Payment.objects.filter(
            user=user,
            course=course,
            is_paid=True
        ).exists()

        if existing_payment:
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
                "message": "Ссылка для оплаты создана"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentSuccessAPIView(views.APIView):
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
        return Response({"message": "Оплата прошла успешно! Спасибо за покупку."})


class PaymentCancelAPIView(views.APIView):
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


class PaymentStatusAPIView(views.APIView):
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

            # Получаем статус из Stripe
            session = get_stripe_session_status(session_id)

            # Обновляем статус платежа в нашей системе
            if session.payment_status == 'paid' and not payment.is_paid:
                payment.is_paid = True
                payment.save()

            return Response({
                "payment_id": payment.id,
                "status": session.payment_status,
                "paid": session.payment_status == 'paid',
                "amount": float(payment.amount),
                "course": payment.course.title if payment.course else None
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )