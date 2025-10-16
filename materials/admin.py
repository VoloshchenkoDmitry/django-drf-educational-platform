from django.contrib import admin
from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'price', 'lessons_count')
    search_fields = ('title',)
    inlines = [LessonInline]

    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'Количество уроков'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner')
    list_filter = ('course',)
    search_fields = ('title', 'description')