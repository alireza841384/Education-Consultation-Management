from rest_framework.permissions import SAFE_METHODS, BasePermission

from Accounts.models import CustomUser


class IsAdmin(BasePermission):
    message = "Admin access is required to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.type == CustomUser.Types.ADMIN
        )


class IsScheduleAdvisorOwnerOrAdmin(BasePermission):
    message = "Only the advisor who owns this schedule can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.type == CustomUser.Types.ADMIN:
            return True

        return obj.advisor_id == request.user.id


class IsSlotAdvisorOwnerOrAdmin(BasePermission):
    message = "Only the advisor who owns this slot can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.type == CustomUser.Types.ADMIN:
            return True

        return obj.schedule.advisor_id == request.user.id

class IsAdvisorOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        return (
            request.user.is_authenticated
            and request.user.type == CustomUser.Types.ADMIN
        )