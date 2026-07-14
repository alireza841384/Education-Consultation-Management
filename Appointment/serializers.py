from django.utils import timezone

from rest_framework import serializers

from .models import AppointmentSlot, Schedule , Appointment


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule

        fields = [
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        if self.instance:
            start_date = attrs.get(
                "start_date",
                self.instance.start_date,
            )

            end_date = attrs.get(
                "end_date",
                self.instance.end_date,
            )
        else:
            start_date = attrs["start_date"]
            end_date = attrs["end_date"]

        if start_date > end_date:
            raise serializers.ValidationError(
                {
                    "end_date": "End date must be after start date."
                }
            )

        if start_date < timezone.localdate():
            raise serializers.ValidationError(
                {
                    "start_date": "Start date cannot be in the past."
                }
            )

        advisor = self.context["request"].user

        schedules = Schedule.objects.filter(
            advisor=advisor,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if self.instance:
            schedules = schedules.exclude(
                pk=self.instance.pk,
            )

        if schedules.exists():
            raise serializers.ValidationError(
                {
                    "start_date": "This schedule overlaps with another schedule."
                }
            )

        return attrs


class AppointmentSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentSlot

        fields = [
            "date",
            "start_time",
            "end_time",
            "status",
        ]

        read_only_fields = [
            "status",
        ]

    def validate(self, attrs):

        schedule = self.context["schedule"]

        if self.instance:
            date = attrs.get("date", self.instance.date)
            start_time = attrs.get(
                "start_time",
                self.instance.start_time,
            )
            end_time = attrs.get(
                "end_time",
                self.instance.end_time,
            )
        else:
            date = attrs["date"]
            start_time = attrs["start_time"]
            end_time = attrs["end_time"]

        if date < timezone.localdate():
            raise serializers.ValidationError(
                {
                    "date": "Appointment date cannot be in the past."
                }
            )

        if start_time >= end_time:
            raise serializers.ValidationError(
                {
                    "end_time": "End time must be after start time."
                }
            )

        if not (
            schedule.start_date <= date <= schedule.end_date
        ):
            raise serializers.ValidationError(
                {
                    "date": (
                        "Appointment date must be within the "
                        "schedule date range."
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
                        "Appointment start time cannot be in the past."
                    )
                }
            )

        slots = AppointmentSlot.objects.filter(
            schedule=schedule,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance:
            slots = slots.exclude(
                pk=self.instance.pk,
            )

        if slots.exists():
            raise serializers.ValidationError(
                {
                    "start_time": (
                        "This appointment slot overlaps with "
                        "another slot."
                    )
                }
            )

        return attrs

class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment

        fields = []

    def validate(self, attrs):

        slot = self.context["slot"]
        student = self.context["request"].user

        if slot.status != slot.SlotStatus.AVAILABLE:
            raise serializers.ValidationError(
                {
                    "slot": "This appointment slot is not available."
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
                    "slot": "This appointment slot has already started."
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
                        "at this time."
                    )
                }
            )

        return attrs