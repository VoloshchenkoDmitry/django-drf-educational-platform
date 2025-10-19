from django.contrib import admin
from .models import Course, Lesson, Subscription, CourseUpdate


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1


class CourseUpdateInline(admin.TabularInline):
    model = CourseUpdate
    extra = 0
    readonly_fields = ('updated_at',)
    can_delete = False


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'price', 'lessons_count', 'updates_count')
    search_fields = ('title',)
    inlines = [LessonInline, SubscriptionInline, CourseUpdateInline]

    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'Количество уроков'

    def updates_count(self, obj):
        return obj.updates.count()

    updates_count.short_description = 'Обновления'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner')
    list_filter = ('course',)
    search_fields = ('title', 'description')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'subscribed_at')
    list_filter = ('course', 'subscribed_at')
    search_fields = ('user__email', 'course__title')


@admin.register(CourseUpdate)
class CourseUpdateAdmin(admin.ModelAdmin):
    list_display = ('course', 'update_type', 'updated_at')
    list_filter = ('update_type', 'updated_at', 'course')
    search_fields = ('course__title', 'description')
    readonly_fields = ('updated_at',)
    date_hierarchy = 'updated_at'