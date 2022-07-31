from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrAdminOrReadOnly(BasePermission):
    """
    Права доступа для автора и аутентифицированного пользователя.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            obj.author == request.user
            or request.user.is_staff)
