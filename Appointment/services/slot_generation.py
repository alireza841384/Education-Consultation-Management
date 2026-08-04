from datetime import timedelta, datetime, time, date
from django.db import transaction
from ..models import AppointmentSlot, Schedule

class SlotGenerationService:
    @staticmethod
    def generate_slots(
        schedule: Schedule, 
        slot_duration: int, 
        break_duration: int, 
        max_slots: int | None, 
        ranges: list[dict]
    ) -> dict:
        existing_slots = set(
            AppointmentSlot.objects.filter(schedule=schedule)
            .values_list('date', 'start_time')
        )
        
        slots_to_create = []
        stats = {
            'total_requested': 0,
            'created_count': 0,
            'duplicates_count': 0
        }
        
        step = slot_duration + break_duration
        current_date = schedule.start_date
        processed_ranges = []
        for r in ranges:
            start_m = r['start_time'].hour * 60 + r['start_time'].minute
            end_m = r['end_time'].hour * 60 + r['end_time'].minute
            processed_ranges.append((start_m, end_m))

        with transaction.atomic():
            while current_date <= schedule.end_date:
                for start_m, end_m in processed_ranges:
                    current_range_time = start_m
                    
                    while current_range_time + slot_duration <= end_m:
                        if max_slots is not None and stats['total_requested'] >= max_slots:
                            return stats
                        stats['total_requested'] += 1
                        slot_start_dt = time(hour=current_range_time // 60, minute=current_range_time % 60)
                        
                        end_minutes = current_range_time + slot_duration
                        slot_end_dt = time(hour=end_minutes // 60, minute=end_minutes % 60)
                        if (current_date, slot_start_dt) in existing_slots:
                            stats['duplicates_count'] += 1
                        else:
                            slots_to_create.append(
                                AppointmentSlot(
                                    schedule=schedule,
                                    date=current_date,
                                    start_time=slot_start_dt,
                                    end_time=slot_end_dt,
                                    status=AppointmentSlot.SlotStatus.AVAILABLE
                                )
                            )
                            stats['created_count'] += 1
                            existing_slots.add((current_date, slot_start_dt))
                        current_range_time += step
        
                current_date += timedelta(days=1)
            if slots_to_create:
                AppointmentSlot.objects.bulk_create(slots_to_create)
                
        return stats
