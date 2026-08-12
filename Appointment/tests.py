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

        cls.schedule = Schedule.objects.create(
            advisor=cls.advisor,
            start_date=timezone.localdate() + timedelta(days=1),
            end_date=timezone.localdate() + timedelta(days=2),
        )

    def setUp(self):
        self.client.force_authenticate(user=None)

    def create_slot(self, status=AppointmentSlot.SlotStatus.AVAILABLE):
        return AppointmentSlot.objects.create(
            schedule=self.schedule,
            date=timezone.localdate() + timedelta(days=1),
            start_time="10:00",
            end_time="11:00",
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

    def test_student_cannot_cancel_slot(self):
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

        Appointment.objects.create(
            slot=slot,
            student=self.student,
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
    # ADVISOR
    # =========================================================

    def test_advisor_can_cancel_booked_slot_and_appointment(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.BOOKED
        )

        appointment = Appointment.objects.create(
            slot=slot,
            student=self.student,
            status=Appointment.AppointmentStatus.BOOKED,
        )

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

        appointment = Appointment.objects.create(
            slot=slot,
            student=self.student,
            status=Appointment.AppointmentStatus.BOOKED,
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

        self.assertEqual(
            appointment.status,
            Appointment.AppointmentStatus.CANCELED,
        )

    def test_advisor_can_make_canceled_slot_available(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.CANCELED
        )

        appointment = Appointment.objects.create(
            slot=slot,
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

        slot.refresh_from_db()
        appointment.refresh_from_db()

        self.assertEqual(
            slot.status,
            AppointmentSlot.SlotStatus.AVAILABLE,
        )

        # Appointment must remain canceled.
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
    # OWNERSHIP
    # =========================================================

    def test_other_advisor_cannot_change_slot(self):
        other_advisor = CustomUser.objects.create_user(
            email="other_advisor@gmail.com",
            password="YOUR_PASSWORD_HERE",
            type=CustomUser.Types.ADMIN,
        )

        slot = self.create_slot()

        self.client.force_authenticate(
            user=other_advisor
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

    # =========================================================
    # RE-BOOKING
    # =========================================================

    def test_student_can_rebook_canceled_appointment(self):
        slot = self.create_slot(
            AppointmentSlot.SlotStatus.CANCELED
        )

        appointment = Appointment.objects.create(
            slot=slot,
            student=self.student,
            status=Appointment.AppointmentStatus.CANCELED,
        )

        self.client.force_authenticate(
            user=self.advisor
        )

        # Advisor makes slot available.
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

        # Student books again.
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

        # Still only ONE appointment.
        self.assertEqual(
            Appointment.objects.filter(
                slot=slot
            ).count(),
            1,
        )