from rest_framework import permissions
from .models import Manager


class IsManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.status == 3 and Manager.objects.filter(restaurant_id=obj.id).exists():
            return True
        return False

    def has_permission(self, request, view):
        if request.user.status == 3:
            return True
        return False


class IsManagerOrAdministrator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.status == 4:
            return True
        return False

    def has_permission(self, request, view):

        if request.user.status == 4:
            return True
        return False
