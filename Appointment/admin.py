from django.contrib import admin

from Accounts.models import CustomUser

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "advisor":
            kwargs["queryset"] = CustomUser.objects.exclude(
                type=CustomUser.Types.STUDENT
            )
        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
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
