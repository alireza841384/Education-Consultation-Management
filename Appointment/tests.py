from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from Accounts.models import CustomUser
from Appointment.models import Schedule, AppointmentSlot, Appointment


class ChangeSlotStatusAPITest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.advisor = CustomUser.objects.create_user(
            email="first_test@gmail.com",
            password="YOUR_PASSWORD_HERE",
            type=CustomUser.Types.ADMIN,
        )

        cls.student = CustomUser.objects.create_user(
            email="second_test@gmail.com",
            password="YOUR_PASSWORD_HERE",
            type=CustomUser.Types.STUDENT,
        )

        cls.other_student = CustomUser.objects.create_user(
            email="third_test@gmail.com",
            password="YOUR_PASSWORD_HERE",
            type=CustomUser.Types.STUDENT,
        )

        cls.other_advisor = CustomUser.objects.create_user(
            email="other_advisor@gmail.com",
            password="YOUR_PASSWORD_HERE",
            type=CustomUser.Types.ADMIN,
        )

        cls.schedule = Schedule.objects.create(
            advisor=cls.advisor,
            start_date=timezone.localdate() + timedelta(days=1),
            end_date=timezone.localdate() + timedelta(days=2),
        )

        cls.other_schedule = Schedule.objects.create(
            advisor=cls.other_advisor,
            start_date=timezone.localdate() + timedelta(days=1),
            end_date=timezone.localdate() + timedelta(days=2),
        )

    def setUp(self):
        self.client.force_authenticate(user=None)

    # =========================================================
    # HELPERS
    # =========================================================

    def create_slot(
        self,
        status=AppointmentSlot.SlotStatus.AVAILABLE,
        schedule=None,
        days_from_now=1,
    ):
        return AppointmentSlot.objects.create(
            schedule=schedule or self.schedule,
            date=timezone.localdate() + timedelta(
                days=days_from_now
            ),
            start_time="10:00",
            end_time="11:00",
            status=status,
        )

    def create_appointment(
        self,
        slot,
        student=None,
        status=Appointment.AppointmentStatus.BOOKED,
    ):
        return Appointment.objects.create(
            slot=slot,
            student=student or self.student,
            status=status,
        )

    def change_status(self, slot, new_status):
        url = reverse(
            "Appointment:change-slot-status",
            kwargs={
                "slot_id": slot.id,
            },
        )

        return self.client.patch(
            url,
            {
                "status": new_status,
            },
            format="json",
        )

    # =========================================================
    # STUDENT
    # =========================================================

    def test_student_can_book_available_slot(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        appointment = Appointment.objects.get(
            slot=slot
        )

        self.assertEqual(
            appointment.student,
            self.student,
        )

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.BOOKED,
        )

    def test_student_cannot_cancel_available_slot(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertFalse(
            Appointment.objects.filter(
                slot=slot
            ).exists()
        )

    def test_student_cannot_book_booked_slot(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_student_cannot_make_booked_slot_available(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.BOOKED,
        )

    def test_student_cannot_cancel_booked_slot(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.BOOKED,
        )

    def test_student_cannot_change_canceled_slot_to_booked(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.CANCELED
        )

        self.create_appointment(
            slot,
            status=Appointment.AppointmentStatus.CANCELED,
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        # طبق منطق فعلی، دانش‌آموز فقط می‌تواند
        # available -> booked را انجام دهد.
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =========================================================
    # ADVISOR
    # =========================================================

    def test_advisor_can_cancel_booked_slot_and_appointment(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        appointment = self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.CANCELED,
        )

    def test_advisor_can_make_booked_slot_available(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        appointment = self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.CANCELED,
        )

    def test_advisor_can_make_canceled_slot_available(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.CANCELED
        )

        appointment = self.create_appointment(
            slot,
            status=Appointment.AppointmentStatus.CANCELED,
        )

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        # Appointment قبلی نباید دوباره BOOKED شود.
        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.CANCELED,
        )

    def test_advisor_cannot_make_available_slot_booked(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertFalse(
            Appointment.objects.filter(
                slot=slot
            ).exists()
        )

    # =========================================================
    # ADVISOR OWNERSHIP
    # =========================================================

    def test_other_advisor_cannot_change_slot(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.other_advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

    def test_advisor_can_change_own_slot(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.CANCELED,
        )

    # =========================================================
    # OTHER STUDENT / EXISTING APPOINTMENT
    # =========================================================

    def test_student_cannot_book_slot_with_another_students_active_appointment(
        self,
    ):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        self.create_appointment(
            slot,
            student=self.other_student,
            status=Appointment.AppointmentStatus.BOOKED,
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =========================================================
    # RE-BOOKING
    # =========================================================

    def test_student_can_rebook_canceled_appointment(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.CANCELED
        )

        appointment = self.create_appointment(
            slot,
            student=self.student,
            status=Appointment.AppointmentStatus.CANCELED,
        )

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.BOOKED,
        )

        self.assertEqual(
            appointment.student,
            self.student,
        )

        self.assertEqual(
            Appointment.objects.filter(
                slot=slot
            ).count(),
            1,
        )

    # =========================================================
    # PAST SLOTS
    # =========================================================

    def test_student_cannot_change_past_slot(self):
        slot = self.create_slot(
            days_from_now=-1
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

    def test_advisor_cannot_change_past_slot(self):
        slot = self.create_slot(
            status=AppointmentSlot.SlotStatus.BOOKED,
            days_from_now=-1,
        )

        self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.BOOKED,
        )

    # =========================================================
    # AUTHENTICATION
    # =========================================================

    def test_anonymous_user_cannot_change_slot(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=None
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.BOOKED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

    # =========================================================
    # INVALID STATUS
    # =========================================================

    def test_invalid_status_is_rejected(self):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.student
        )

        response = self.change_status(
            slot,
            "invalid_status",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        slot.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertFalse(
            Appointment.objects.filter(
                slot=slot
            ).exists()
        )

    # =========================================================
    # APPOINTMENT / SLOT CONSISTENCY
    # =========================================================

    def test_canceling_booked_slot_cancels_active_appointment(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        appointment = self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.CANCELED,
        )

    def test_making_booked_slot_available_cancels_appointment(
        self,
    ):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        appointment = self.create_appointment(slot)

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.CANCELED,
        )

    # =========================================================
    # NO UNEXPECTED APPOINTMENT CREATION
    # =========================================================

    def test_advisor_canceling_available_slot_does_not_create_appointment(
        self,
    ):
        slot = self.create_slot()

        self.client.force_authenticate(
            user=self.advisor
        )

        response = self.change_status(
            slot,
            AppointmentSlot.SlotStatus.CANCELED,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            Appointment.objects.filter(
                slot=slot
            ).exists()
        )