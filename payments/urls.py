from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentListAPIView,
    PaymentCreateAPIView,
    PaymentSuccessAPIView,
    PaymentCancelAPIView,
    PaymentStatusAPIView,
    SubscriptionViewSet,
    UserPaymentHistoryAPIView
)

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    # Payments
    path('', PaymentListAPIView.as_view(), name='payment-list'),
    path('create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
    path('status/', PaymentStatusAPIView.as_view(), name='payment-status'),
    path('history/', UserPaymentHistoryAPIView.as_view(), name='payment-history'),

    # Subscriptions
    path('', include(router.urls)),
]