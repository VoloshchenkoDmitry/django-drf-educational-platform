from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from payments.models import Payment, Subscription
from payments.serializers import PaymentHistorySerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'city')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    payment_history = PaymentHistorySerializer(many=True, read_only=True, source='payments')
    active_subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar',
                  'payment_history', 'active_subscriptions')
        read_only_fields = ('id',)

    def get_active_subscriptions(self, obj):
        return obj.subscriptions.filter(is_active=True).count()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_staff')
        read_only_fields = ('id', 'is_staff')


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'city', 'avatar')
        read_only_fields = fields