from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from Accounts.models import CustomUser
from .models import Report
from .permissions import IsReportOwnerOrAssignedAdvisor
from .serializers import ReportSerializer


class ReportingViewSet(viewsets.ModelViewSet):
    serializer_class=ReportSerializer
    permission_classes=[
        IsAuthenticated,
        IsReportOwnerOrAssignedAdvisor,
    ]

    def get_queryset(self):
        user=self.request.user

        queryset=Report.objects.select_related(
            "user",
            "user__profile",
            "user__profile__advisor",
        )

        
        if user.is_superuser:
            return queryset

        
        if user.type==CustomUser.Types.STUDENT:
            return queryset.filter(user=user)

        
        if user.type==CustomUser.Types.ADMIN:
            return queryset.filter(user__profile__advisor=user)

        return Report.objects.none()

    def perform_create(self,serializer):
        user=self.request.user

        if user.type!=CustomUser.Types.STUDENT:
            raise PermissionDenied(
                "Only students can create reports."
            )

        
        if not hasattr(user,"profile") or user.profile.advisor is None:
            raise PermissionDenied(
                "You do not have an assigned advisor."
            )

        serializer.save(user=user)

    def perform_update(self,serializer):
        report=self.get_object()
        user=self.request.user

        
        if user.type!=CustomUser.Types.STUDENT:
            raise PermissionDenied(
                "Advisors cannot edit student reports."
            )

        if report.user_id!=user.id:
            raise PermissionDenied(
                "You can only edit your own reports."
            )

        serializer.save()

    def perform_destroy(self,instance):
        user=self.request.user

        
        if user.is_superuser:
            instance.delete()
            return

        
        if user.type==CustomUser.Types.STUDENT and instance.user_id==user.id:
            instance.delete()
            return

        raise PermissionDenied(
            "You do not have permission to delete this report."
        )
