from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from Accounts.models import CustomUser
from Accounts.permissions import IsAdvisorOwner
from Appointment.serializers.actions import GenerateSlotsSerializer
from Appointment.serializers.appointment_slot import AppointmentSlotSerializer
from Appointment.serializers.schedule import ScheduleSerializer
from Appointment.utils.mixins import BulkDeleteSlotMixin

from .models import AppointmentSlot, Schedule


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related("advisor")
    permission_classes = (IsAdvisorOwner,)

    def get_queryset(self):
        user = self.request.user

        if user.type == CustomUser.Types.ADMIN:
            return self.queryset.filter(
                advisor=user,
            )

        return self.queryset.filter(
            status=Schedule.Status.PUBLISHED,
        )

    def get_serializer_class(self):
        if self.action == "generate_slots":
            return GenerateSlotsSerializer

        return ScheduleSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, "action", None) == "generate_slots":
            context["schedule"] = self.get_object()

        return context

    def perform_create(self, serializer):
        serializer.save(
            advisor=self.request.user,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="generate-slots",
    )
    def generate_slots(self, request, *args, **kwargs):
        schedule = self.get_object()

        if schedule.status != Schedule.Status.DRAFT:
            return Response(
                {
                    "detail": (
                        "Slots can only be generated for "
                        "schedules in DRAFT status."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )
        try:
            result = SlotGenerationService.generate_slots(
                schedule=schedule,
                **serializer.validated_data,
            )
        except ValueError as error:
            raise serializers.ValidationError(
                {
                    "detail": str(error),
                }
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


class SlotViewSet(BulkDeleteSlotMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = AppointmentSlot.objects.select_related("schedule", "schedule__advisor")
    serializer_class = AppointmentSlotSerializer
    permission_classes = (IsAdvisorOwner,)

    def get_queryset(self):
        user = self.request.user

        if user.type == CustomUser.Types.ADMIN:
            return self.queryset.filter(schedule__advisor=user)

        return self.queryset.filter(
            schedule__advisor=user.profile.advisor,
            schedule__status=Schedule.Status.PUBLISHED,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["schedule"] = get_object_or_404(Schedule, pk=self.kwargs["schedule_pk"])
        return context

    def perform_destroy(self, instance):
        if instance.schedule.status != Schedule.Status.DRAFT:
            raise serializers.ValidationError(
                "Slots can only be deleted from a draft schedule."
            )
        instance.delete()