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
        model = Appointment
        fields = ["date", "start_time", "end_time"]
    
    def validate(self, attrs):
        if attrs["date"] < timezone.localdate():
            raise serializers.ValidationError(
                {
                    "date": "Appointment date cannot be in the past."
                }
            )
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError(
                {
                    "end_time": "End time must be after start time."
                }
            )
        if attrs["date"] > self.context["schedule"].end_date or attrs["date"] < self.context["schedule"].start_date:
            raise serializers.ValidationError(
                {
                    "date": "Appointment date must be within the schedule's date range."
                }
            )
        if Appointment.objects.filter(
            schedule=self.context["schedule"],
            date=attrs["date"],
            start_time__lt=attrs["end_time"],
            end_time__gt=attrs["start_time"],
        ).exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": "This appointment slot overlaps with another slot."
                }
            )
        if attrs["start_time"] < timezone.now().time() and attrs["date"] == timezone.localdate():
            raise serializers.ValidationError(
                {
                    "start_time": "Appointment start time cannot be in the past."
                }
            )

        return  attrs