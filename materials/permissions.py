from rest_framework import permissions


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Permission для проверки владельца или модератора
    """

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderators').exists():
            return True
        return obj.owner == request.user


class CanCreateLesson(permissions.BasePermission):
    """
    Permission для создания уроков (только обычные пользователи, не модераторы)
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return (request.user.is_authenticated and
                    not request.user.groups.filter(name='moderators').exists())
        return True


class CanCreateCourse(permissions.BasePermission):
    """
    Permission для создания курсов (только обычные пользователи, не модераторы)
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return (request.user.is_authenticated and
                    not request.user.groups.filter(name='moderators').exists())
        return True


# Для ViewSet оставляем старые permissions
class CoursePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, 'action'):
            if view.action == 'create':
                return request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(view, 'action'):
            action = view.action
        else:
            # Для APIView определяем action по методу
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                action = 'retrieve'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'destroy'
            else:
                action = None

        if action in ['retrieve', 'update', 'partial_update']:
            if request.user.groups.filter(name='moderators').exists():
                return True
            return obj.owner == request.user
        elif action == 'destroy':
            return obj.owner == request.user

        return True


class LessonPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, 'action'):
            if view.action == 'create':
                return request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(view, 'action'):
            action = view.action
        else:
            # Для APIView определяем action по методу
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                action = 'retrieve'
            elif request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'destroy'
            else:
                action = None

        if action in ['retrieve', 'update', 'partial_update']:
            if request.user.groups.filter(name='moderators').exists():
                return True
            return obj.owner == request.user
        elif action == 'destroy':
            return obj.owner == request.user

        return True