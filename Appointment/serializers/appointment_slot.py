from django.utils import timezone
from rest_framework import serializers

from Appointment.models import AppointmentSlot


class AppointmentSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentSlot
        fields = (
            "id",
            "date",
            "start_time",
            "end_time",
            "date_start",
            "date_end",
            "status",
        )

        read_only_fields = (
            "id",
        )

    def validate(self, attrs):
        schedule = self.context["schedule"]

        instance = self.instance

        date = attrs.get(
            "date",
            instance.date if instance else None,
        )

        start_time = attrs.get(
            "start_time",
            instance.start_time if instance else None,
        )

        end_time = attrs.get(
            "end_time",
            instance.end_time if instance else None,
        )

        status = attrs.get(
            "status",
            instance.status if instance else AppointmentSlot.Status.AVAILABLE,
        )

        today = timezone.localdate()

        if date < today:
            raise serializers.ValidationError(
                {
                    "date": (
                        "Appointment date cannot be in the past."
                    )
                }
            )

        if start_time >= end_time:
            raise serializers.ValidationError(
                {
                    "end_time": (
                        "End time must be after start time."
                    )
                }
            )

        if not (
            schedule.start_date
            <= date
            <= schedule.end_date
        ):
            raise serializers.ValidationError(
                {
                    "date": (
                        "Appointment date must be within "
                        "the schedule date range."
                    )
                }
            )

        now = timezone.localtime()

        if (
            date == now.date()
            and start_time < now.time()
        ):
            raise serializers.ValidationError(
                {
                    "start_time": (
                        "Appointment start time cannot "
                        "be in the past."
                    )
                }
            )

        if status not in AppointmentSlot.Status.values:
            raise serializers.ValidationError(
                {
                    "status": "Invalid slot status."
                }
            )

        queryset = AppointmentSlot.objects.filter(
            schedule=schedule,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "start_time": (
                        "This appointment slot overlaps "
                        "with another slot."
                    )
                }
            )

        return attrs

