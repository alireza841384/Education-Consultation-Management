from rest_framework.permissions import BasePermission , SAFE_METHODS
from .models import CustomUser

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == CustomUser.Types.ADMIN

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == CustomUser.Types.STUDENT

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.type == CustomUser.Types.ADMIN:
            return True
        return obj.user == request.user

class IsAdvisorOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        return (
            request.user.is_authenticated
            and request.user.type == CustomUser.Types.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.advisor == request.user