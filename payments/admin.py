from django.contrib import admin
from .models import Payment, Subscription


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'course', 'lesson', 'amount', 'payment_method', 'status')
    list_filter = ('payment_method', 'status', 'payment_date', 'course')
    search_fields = ('user__email', 'course__title', 'lesson__title')
    readonly_fields = ('payment_date', 'stripe_product_id', 'stripe_price_id', 'stripe_session_id')
    date_hierarchy = 'payment_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course', 'lesson')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at', 'course')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('subscribed_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')