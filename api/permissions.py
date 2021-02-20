from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or
            (hasattr(obj, 'author') and obj.author == request.user) or
            (hasattr(obj, 'user') and obj.user == request.user)
        )
