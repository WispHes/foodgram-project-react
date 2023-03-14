from rest_framework import permissions


class AuthorPermission(permissions.BasePermission):
    """Авторские права на изменение и добавление"""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
