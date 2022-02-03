from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user:
            return obj.author == request.user
