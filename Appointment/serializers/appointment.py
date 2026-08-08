
from django.utils import timezone
from rest_framework import serializers

from Appointment.models import Appointment, AppointmentSlot


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