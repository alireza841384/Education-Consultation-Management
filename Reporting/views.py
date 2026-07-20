from rest_framework.generics import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from Accounts.models import CustomUser
from .serializers import ReportingSerializer
from .models import Report

class ReportingViewSet(ModelViewSet):
    serializer_class = ReportingSerializer
    permission_classes = [IsAuthenticated]
    query_set = Report.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.type == CustomUser.Types.ADMIN:
            return Report.objects.all()
        return Report.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)