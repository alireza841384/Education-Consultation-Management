from django.contrib import admin

from .models import Appointment, AppointmentSlot, Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "advisor",
        "start_date",
        "end_date",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "start_date",
        "end_date",
    )
    search_fields = (
        "advisor__email",
    )
    ordering = (
        "-start_date",
    )


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = (
        "schedule",
        "date",
        "start_time",
        "end_time",
        "status",
    )
    list_filter = (
        "status",
        "date",
    )
    search_fields = (
        "schedule__advisor__email",
    )
    ordering = (
        "date",
        "start_time",
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "slot",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "student__email",
        "slot__schedule__advisor__email",
    )
    ordering = (
        "-created_at",
    )
