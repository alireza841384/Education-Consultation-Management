from Accounts.models import CustomUser

from .serializers import AppointmentSerializer , ScheduleSerializer, AppointmentSlotSerializer
from .models import Appointment, Schedule, AppointmentSlot
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.type == CustomUser.Types.ADMIN:
            return Schedule.objects.all()
        return Schedule.objects.filter(advisor=user)
    
    def perform_create(self, serializer):
        serializer.save(advisor=self.request.user)