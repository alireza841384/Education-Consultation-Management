from django.http import HttpResponseForbidden

from Accounts.models import CustomUser

from .serializers import AppointmentSerializer , ScheduleSerializer, AppointmentSlotSerializer
from .models import Appointment, Schedule, AppointmentSlot
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from Accounts.permissions import IsAdvisorOwner

class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdvisorOwner]
    queryset = Schedule.objects.select_related("advisor")

    def get_queryset(self):
        user = self.request.user

        if user.type == CustomUser.Types.ADMIN:
            return self.queryset.filter(advisor=user)

        advisor = user.profile.advisor

        if advisor is None:
            return self.queryset.none()

        return self.queryset.filter(
            advisor=advisor,
        )

    def perform_create(self, serializer):
        serializer.save(
            advisor=self.request.user,
        )


