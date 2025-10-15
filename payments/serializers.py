from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = (
            'id', 'user', 'payment_date', 'stripe_product_id',
            'stripe_price_id', 'stripe_session_id', 'payment_url', 'is_paid'
        )


class PaymentHistorySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'payment_date', 'course', 'lesson', 'course_title', 'lesson_title',
                  'amount', 'payment_method', 'is_paid')
        read_only_fields = fields