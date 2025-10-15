from django.urls import path
from .views import (
    LessonListCreateAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionAPIView,
    PaymentCreateAPIView,
    PaymentSuccessAPIView,
    PaymentCancelAPIView,
    PaymentStatusAPIView,
    PaymentTestInfoAPIView
)

urlpatterns = [
    # Lessons
    path('', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),

    # Subscriptions
    path('subscription/', SubscriptionAPIView.as_view(), name='subscription'),

    # Payments
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payments/success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('payments/cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
    path('payments/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
    path('payments/test-info/', PaymentTestInfoAPIView.as_view(), name='payment-test-info'),
]