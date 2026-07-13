from django.db import models

from Accounts.models import CustomUser


class Schedule(models.Model):
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

    def __str__(self):
        return (
            f"{self.advisor.email} | "
            f"{self.start_date} -> {self.end_date}"
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
        ordering = [
            "date",
            "start_time",
        ]

    def __str__(self):
        return (
            f"{self.date} | "
            f"{self.start_time}-{self.end_time}"
        )

class Appointment(models.Model):

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    slot = models.OneToOneField(
        AppointmentSlot,
        on_delete=models.CASCADE,
        related_name="appointment",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now_add=True,
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