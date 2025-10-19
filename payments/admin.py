from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'course', 'lesson', 'amount', 'payment_method', 'is_paid')
    list_filter = ('payment_method', 'payment_date', 'course', 'is_paid')
    search_fields = ('user__email', 'course__title', 'lesson__title')
    readonly_fields = ('payment_date', 'stripe_product_id', 'stripe_price_id', 'stripe_session_id')
    date_hierarchy = 'payment_date'