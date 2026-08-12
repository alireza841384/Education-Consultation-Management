from datetime import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from Accounts.models import CustomUser
from ..models import Appointment
from ..models import AppointmentSlot


class SlotStatusService:

    @staticmethod
    @transaction.atomic
    def change_status(
        *,
        slot_id: int,
        user,
        new_status: str,
    ):
        slot = (
            AppointmentSlot.objects
            .select_for_update()
            .select_related("schedule")
            .get(pk=slot_id)
        )

        if user.type == CustomUser.Types.ADMIN:

            if slot.schedule.advisor_id != user.id:
                raise ValidationError(
                    {
                        "detail": (
                            "You can only change slots "
                            "from your own schedules."
                        )
                    }
                )

        slot_datetime = timezone.make_aware(
            datetime.combine(
                slot.date,
                slot.start_time,
            )
        )

        if slot_datetime <= timezone.now():
            raise ValidationError(
                {
                    "detail": "Past slots cannot be changed."
                }
            )

        if user.type == CustomUser.Types.STUDENT:
            if (
                slot.status
                != AppointmentSlot.SlotStatus.AVAILABLE
            ):
                raise ValidationError(
                    {
                        "detail": (
                            "Students can only book "
                            "available slots."
                        )
                    }
                )

            if (
                new_status
                != AppointmentSlot.SlotStatus.BOOKED
            ):
                raise ValidationError(
                    {
                        "detail": (
                            "Students can only change "
                            "available slots to booked."
                        )
                    }
                )

            appointment = (
                Appointment.objects
                .select_for_update()
                .filter(slot=slot)
                .first()
            )

            if appointment is None:

                appointment = Appointment.objects.create(
                    slot=slot,
                    student=user,
                    status=(
                        Appointment.AppointmentStatus.BOOKED
                    ),
                )

            else:

                if (
                    appointment.status
                    != Appointment.AppointmentStatus.CANCELED
                ):
                    raise ValidationError(
                        {
                            "detail": (
                                "This slot already has "
                                "an active appointment."
                            )
                        }
                    )

                appointment.student = user
                appointment.status = (
                    Appointment.AppointmentStatus.BOOKED
                )

                appointment.save(
                    update_fields=[
                        "student",
                        "status",
                        "updated_at",
                    ]
                )
            slot.status = (
                AppointmentSlot.SlotStatus.BOOKED
            )

            slot.save(
                update_fields=["status"]
            )

            return slot

        if user.type == CustomUser.Types.ADMIN:

            if (
                new_status
                == AppointmentSlot.SlotStatus.BOOKED
            ):
                raise ValidationError(
                    {
                        "status": (
                            "A slot can only become "
                            "booked when a student "
                            "books it."
                        )
                    }
                )

            if (
                slot.status
                == AppointmentSlot.SlotStatus.BOOKED
                and new_status
                in (
                    AppointmentSlot.SlotStatus.CANCELED,
                    AppointmentSlot.SlotStatus.AVAILABLE,
                )
            ):

                Appointment.objects.filter(
                    slot=slot,
                    status=(
                        Appointment.AppointmentStatus.BOOKED
                    ),
                ).update(
                    status=(
                        Appointment.AppointmentStatus.CANCELED
                    )
                )

            slot.status = new_status

            slot.save(
                update_fields=["status"]
            )

            return slot

        raise ValidationError(
            {
                "detail": (
                    "You do not have permission "
                    "to change this slot."
                )
            }
        )