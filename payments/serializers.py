from rest_framework import serializers
from .models import Payment, Subscription


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = (
            'id', 'user', 'payment_date', 'stripe_product_id',
            'stripe_price_id', 'stripe_session_id', 'stripe_payment_intent_id',
            'payment_url', 'status'
        )


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('course', 'lesson', 'amount', 'payment_method')
        extra_kwargs = {
            'course': {'required': False},
            'lesson': {'required': False},
            'amount': {'required': True},
        }

    def validate(self, attrs):
        course = attrs.get('course')
        lesson = attrs.get('lesson')

        if not course and not lesson:
            raise serializers.ValidationError("Необходимо указать курс или урок")

        if course and lesson:
            raise serializers.ValidationError("Можно указать только курс ИЛИ урок")

        return attrs


class SubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'subscribed_at')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('course',)


class PaymentHistorySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'payment_date', 'course', 'lesson', 'course_title',
            'lesson_title', 'amount', 'payment_method', 'status'
        )
        read_only_fields = fields