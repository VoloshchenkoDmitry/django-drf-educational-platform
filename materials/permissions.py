from rest_framework import permissions
from users.permissions import IsModerator


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Проверка, является ли пользователь владельцем или модератором
    """
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderators').exists():
            return True
        return obj.owner == request.user


class CoursePermission(permissions.BasePermission):
    """
    Права доступа для курсов
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'update', 'partial_update']:
            if request.user.groups.filter(name='moderators').exists():
                return True
            return obj.owner == request.user
        elif view.action == 'destroy':
            return obj.owner == request.user
        return True


class LessonPermission(permissions.BasePermission):
    """
    Права доступа для уроков
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'update', 'partial_update']:
            if request.user.groups.filter(name='moderators').exists():
                return True
            return obj.owner == request.user
        elif view.action == 'destroy':
            return obj.owner == request.user
        return True