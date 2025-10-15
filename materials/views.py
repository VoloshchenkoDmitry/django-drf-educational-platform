from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .permissions import CoursePermission, LessonPermission, IsOwnerOrModerator, CanCreateLesson
from .paginators import LessonPaginator, CoursePaginator


# Для ViewSet используем старые permissions
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [CoursePermission]
    pagination_class = CoursePaginator

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


# Для APIView используем новые permissions
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanCreateLesson]
    pagination_class = LessonPaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


# Остальные views...
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

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


# Payment views остаются без изменений...
class PaymentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
        from payments.models import Payment
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
            base_url = request.build_absolute_uri('/')[:-1]
            from .services import create_payment_flow
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


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('payment_id')
        session_id = request.GET.get('session_id')

        if not payment_id and not session_id:
            return Response(
                {"error": "Необходимо указать payment_id или session_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from payments.models import Payment

            if payment_id:
                payment = get_object_or_404(Payment, id=payment_id, user=request.user)
                session_id = payment.stripe_session_id
            else:
                payment = get_object_or_404(Payment, stripe_session_id=session_id, user=request.user)

            from .services import get_stripe_session_status
            session = get_stripe_session_status(session_id)

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


class PaymentTestInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .services import get_test_payment_info
        test_info = get_test_payment_info()

        return Response({
            **test_info,
            'instructions': 'Для тестирования используйте тестовые данные карты'
        })


class PaymentSuccessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата прошла успешно! Спасибо за покупку."})


class PaymentCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата отменена. Вы можете попробовать снова."})