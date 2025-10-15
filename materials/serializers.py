from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_only


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner',)

    def validate_video_link(self, value):
        """
        Валидация ссылки на видео
        """
        if value:
            validate_youtube_only(value)
        return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'preview', 'description', 'price',
            'owner', 'lessons_count', 'lessons', 'is_subscribed'
        ]
        read_only_fields = ('owner',)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на курс
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False