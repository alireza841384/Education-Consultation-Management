from pathlib import Path

from django.conf import settings
from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = [
            "title",
            "description",
            "start_time",
            "end_time",
            "file",
        ]

    def validate(self, attrs):
        start_time = attrs["start_time"]
        end_time = attrs["end_time"]

        if start_time > end_time:
            raise serializers.ValidationError(
                {
                    "end_time": "End date must be after start date."
                }
            )

        return attrs

    def validate_file(self, file):

        if file.size == 0:
            raise serializers.ValidationError(
                "File cannot be empty."
            )

        if file.size > settings.MAX_REPORT_FILE_SIZE:
            raise serializers.ValidationError(
                "File size exceeds the allowed limit."
            )

        extension = Path(file.name).suffix.lower()

        if extension not in settings.ALLOWED_REPORT_EXTENSIONS:
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        if file.content_type != "application/pdf":
            raise serializers.ValidationError(
                "Invalid file type."
            )

        return file