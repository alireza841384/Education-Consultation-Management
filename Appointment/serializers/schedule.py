from rest_framework import serializers

from Appointment.models import Schedule


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

