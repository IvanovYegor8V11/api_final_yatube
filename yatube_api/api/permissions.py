from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class OnlyAuthor(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы (например, GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Убедиться, что пользователь авторизован
        if not request.user.is_authenticated:
            raise PermissionDenied("Пользователь не авторизован.")

        # Разрешить доступ только автору объекта
        return obj.author == request.user


class GroupOnlyGet(permissions.BasePermission):
    """
    Разрешение, которое позволяет только GET-запросы для группы.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Убедиться, что пользователь авторизован
        if not request.user.is_authenticated:
            raise PermissionDenied("Пользователь не авторизован.")

        raise PermissionDenied("Запрещен доступ для данного метода.")
