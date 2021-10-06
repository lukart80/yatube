from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """Permission допускает только безопастные методы для неавторов."""

    def has_permission(self, request, view):
        return (request.method in
                permissions.SAFE_METHODS or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in
                permissions.SAFE_METHODS or request.user == obj.author)


class AuthenticatedOnly(permissions.BasePermission):
    """Permission только для авторизованных пользователей."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated
