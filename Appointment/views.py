from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Schedule
from .serializers import ScheduleSerializer, GenerateSlotsSerializer
from .services.slot_generation import SlotGenerationService


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related("advisor")
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=True,
        methods=["post"],
        url_path="generate-slots",
    )
    def generate_slots(self, request, pk=None):
        schedule = self.get_object()

        if not self._can_manage_schedule(request.user, schedule):
            return Response(
                {
                    "detail": (
                        "You do not have permission to manage this schedule."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if schedule.status != Schedule.Status.DRAFT:
            return Response(
                {
                    "detail": (
                        "Slots can only be generated while the schedule "
                        "is in draft status."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = GenerateSlotsSerializer(
            data=request.data,
            context={
                "request": request,
                "schedule": schedule,
            },
        )
        serializer.is_valid(raise_exception=True)

        result = SlotGenerationService.generate_slots(
            schedule=schedule,
            actor=request.user,
            **serializer.validated_data,
        )

        return Response(
            {
                "schedule_id": schedule.id,
                "created": result["created_count"],
                "duplicates": result["duplicates_count"],
                "total": result["total_requested"],
            },
            status=status.HTTP_201_CREATED,
        )

    def _can_manage_schedule(self, user, schedule):
        return (
            user.is_staff
            or user.is_superuser
            or schedule.advisor_id == user.id
        )
