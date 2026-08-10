from rest_framework.permissions import BasePermission

from Accounts.models import CustomUser


class IsReportOwnerOrAssignedAdvisor(BasePermission):
    def has_object_permission(self,request,view,obj):
        user=request.user

        if user.is_superuser:
            return True

        if user.type==CustomUser.Types.STUDENT:
            return obj.user_id==user.id

        if user.type==CustomUser.Types.ADMIN:
            return obj.user.profile.advisor_id==user.id

        return False
