from django.urls import path
from .views import (
    PaymentListAPIView,
    PaymentCreateAPIView,
    PaymentSuccessAPIView,
    PaymentCancelAPIView,
    PaymentStatusAPIView
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListAPIView.as_view(), name='payment-list'),
    path('create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
    path('status/', PaymentStatusAPIView.as_view(), name='payment-status'),
]