"""
    ├── GenerateSlotsSerializer
    ├── PreviewSlotsSerializer
    ├── CopySlotsSerializer
    ├── BulkStatusSerializer
    ├── BulkDeleteSerializer
    ├── ClearFreeSlotsSerializer
    └── ForceClearSlotsSerializer
"""
from rest_framework import serializers


class TimeRangeSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError(
                {
                    "end_time": (
                        "End time must be greater than start time."
                    )
                }
            )

        return attrs


class GenerateSlotsSerializer(serializers.Serializer):
    slot_duration = serializers.IntegerField(
        min_value=1,
        help_text="Duration of each appointment slot in minutes.",
    )

    break_duration = serializers.IntegerField(
        min_value=0,
        default=0,
        help_text="Break duration between slots in minutes.",
    )

    max_slots = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
        default=None,
        help_text="Maximum number of slots to generate. Leave null for no limit.",
    )

    ranges = TimeRangeSerializer(
        many=True,
        allow_empty=False,
    )

    def validate(self, attrs):
        ranges = attrs["ranges"]
        sorted_ranges = sorted(
            ranges,
            key=lambda item: item["start_time"],
        )
        for current, nxt in zip(sorted_ranges, sorted_ranges[1:]):
            if current["end_time"] > nxt["start_time"]:
                raise serializers.ValidationError(
                    {
                        "ranges": (
                            "Time ranges must not overlap."
                        )
                    }
                )

        return attrs


class CopySlotsSerializer(serializers.Serializer):
    source_date = serializers.DateField(
        help_text="The date whose slots should be copied."
    )

    target_dates = serializers.ListField(
        child=serializers.DateField(),
        allow_empty=False,
        help_text="Dates that will receive copies of the source day's slots.",
    )

    def validate_target_dates(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Target dates must be unique."
            )

        return value

    def validate(self, attrs):
        source_date = attrs["source_date"]
        target_dates = attrs["target_dates"]

        if source_date in target_dates:
            raise serializers.ValidationError(
                {
                    "target_dates": (
                        "Source date cannot be included in target dates."
                    )
                }
            )

        return attrs