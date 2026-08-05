from datetime import time, timedelta

from django.db import transaction
from django.db.models import Q

from ..models import AppointmentSlot
from ..models import Schedule


class SlotGenerationService:
    MINUTES_PER_HOUR = 60

    @staticmethod
    def _time_to_minutes(value: time) -> int:
        return (
            value.hour * SlotGenerationService.MINUTES_PER_HOUR
            + value.minute
        )

    @staticmethod
    def generate_slots(
        *,
        schedule,
        slot_duration,
        break_duration,
        max_slots,
        ranges,
        date_start=None,
        date_end=None,
    ):
        date_start = date_start or schedule.start_date
        date_end = date_end or schedule.end_date

        if date_start > date_end:
            raise ValueError(
                "date_start must be before or equal to date_end."
            )

        if (
            date_start < schedule.start_date
            or date_end > schedule.end_date
        ):
            raise ValueError(
                "The requested date range must be within the schedule date range."
            )

        if slot_duration <= 0:
            raise ValueError("slot_duration must be greater than zero.")

        if break_duration < 0:
            raise ValueError("break_duration cannot be negative.")

        slot_interval = slot_duration + break_duration

        processed_ranges = [
            (
                item["start_time"],
                item["end_time"],
            )
            for item in ranges
        ]

        overlap_query = Q()

        for range_start, range_end in processed_ranges:
            overlap_query |= Q(
                start_time__lt=range_end,
                end_time__gt=range_start,
            )

        has_existing_slots = AppointmentSlot.objects.filter(
            schedule=schedule,
            date__gte=date_start,
            date__lte=date_end,
        ).filter(
            overlap_query
        ).exists()

        if has_existing_slots:
            raise ValueError(
                "Delete the Slots that have overlap"
            )

        processed_ranges = [
            (
                SlotGenerationService._time_to_minutes(
                    item["start_time"]
                ),
                SlotGenerationService._time_to_minutes(
                    item["end_time"]
                ),
            )
            for item in ranges
        ]

        slots_to_create: list[AppointmentSlot] = []

        total_requested = 0
        created_count = 0
        duplicates_count = 0

        reached_limit = False

        current_date = date_start

        with transaction.atomic():
            while current_date <= date_end and not reached_limit:
                total_requested = 0

                for range_start, range_end in processed_ranges:
                    current_minute = range_start

                    while current_minute + slot_duration <= range_end:
                        if (
                            max_slots is not None
                            and total_requested >= max_slots
                        ):
                            reached_limit = True
                            break

                        total_requested += 1

                        start_time = time(
                            hour=current_minute
                            // SlotGenerationService.MINUTES_PER_HOUR,
                            minute=current_minute
                            % SlotGenerationService.MINUTES_PER_HOUR,
                        )

                        end_minutes = current_minute + slot_duration

                        end_time = time(
                            hour=end_minutes
                            // SlotGenerationService.MINUTES_PER_HOUR,
                            minute=end_minutes
                            % SlotGenerationService.MINUTES_PER_HOUR,
                        )

                        slots_to_create.append(
                            AppointmentSlot(
                                schedule=schedule,
                                date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                status=AppointmentSlot.SlotStatus.AVAILABLE,
                            )
                        )

                        created_count += 1
                        current_minute += slot_interval

                    if reached_limit:
                        break

                current_date += timedelta(days=1)

            if slots_to_create:
                AppointmentSlot.objects.bulk_create(
                    slots_to_create,
                    batch_size=1000,
                )

        return {
            "total_requested": total_requested,
            "created_count": created_count,
            "duplicates_count": duplicates_count,
        }
