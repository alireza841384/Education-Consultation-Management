from django.db import models
from django.core.exceptions import ValidationError

from Accounts.models import CustomUser


class Schedule(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    advisor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="schedule_end_after_start",
            ),
        ]

    def __str__(self):
        return (
            f"{self.advisor.email} | "
            f"{self.start_date} -> {self.end_date}"
        )

    def clean(self):
        super().clean()

        if self.advisor_id and self.advisor.type != CustomUser.Types.ADMIN:
            raise ValidationError(
                {"advisor": "The advisor must be an admin user."}
            )


class AppointmentSlot(models.Model):

    class SlotStatus(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        CANCELED = "canceled", "Canceled"

    schedule = models.ForeignKey(
        "Schedule",
        on_delete=models.CASCADE,
        related_name="slots",
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=SlotStatus.choices,
        default=SlotStatus.AVAILABLE,
    )

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "date", "start_time"],
                name="unique_slot_per_schedule",
            ),
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="slot_end_after_start",
            ),
        ]

    def __str__(self):
        return (
            f"{self.date} | "
            f"{self.start_time}-{self.end_time}"
        )

class Appointment(models.Model):
    class AppointmentStatus(models.TextChoices):
        BOOKED = "booked", "Booked"
        CANCELED = "canceled", "Canceled"

    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.BOOKED,
        )

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    slot = models.OneToOneField(
        AppointmentSlot,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.student.email} | "
            f"{self.slot.date} | "
            f"{self.slot.start_time}"
        )