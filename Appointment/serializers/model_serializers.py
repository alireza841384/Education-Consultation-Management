from django.utils import timezone

from rest_framework import serializers

from ..models import Appointment
from ..models import AppointmentSlot
from ..models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = (
            "id",
            "advisor",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "advisor",
            "status",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        instance = self.instance

        advisor = (
            instance.advisor
            if instance
            else self.context["request"].user
        )

        start_date = attrs.get(
            "start_date",
            instance.start_date if instance else None,
        )

        end_date = attrs.get(
            "end_date",
            instance.end_date if instance else None,
        )
        date_start = serializers.DateField(
            required=False,
            allow_null=True,
        )

        date_end = serializers.DateField(
            required=False,
            allow_null=True,
        )


        if start_date > end_date:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "End date must be after start date."
                    )
                }
            )

        overlaps = Schedule.objects.filter(
            advisor=advisor,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if instance:
            overlaps = overlaps.exclude(pk=instance.pk)

        if overlaps.exists():
            raise serializers.ValidationError(
                {
                    "start_date": (
                        "This schedule overlaps with an existing schedule."
                    )
                }
            )

        return attrs


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


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = ()

    def validate(self, attrs):
        slot = self.context["slot"]
        student = self.context["request"].user

        if (
            slot.status
            != AppointmentSlot.Status.AVAILABLE
        ):
            raise serializers.ValidationError(
                {
                    "slot": (
                        "This appointment slot is not available."
                    )
                }
            )

        now = timezone.localtime()

        if (
            slot.date < now.date()
            or (
                slot.date == now.date()
                and slot.start_time <= now.time()
            )
        ):
            raise serializers.ValidationError(
                {
                    "slot": (
                        "This appointment slot has already started."
                    )
                }
            )

        has_overlap = Appointment.objects.filter(
            student=student,
            slot__date=slot.date,
            slot__start_time__lt=slot.end_time,
            slot__end_time__gt=slot.start_time,
        ).exists()

        if has_overlap:
            raise serializers.ValidationError(
                {
                    "slot": (
                        "You already have another appointment "
                        "during this time."
                    )
                }
            )

        return attrs