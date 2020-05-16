from datetime import timedelta

from django.test import TestCase

from edc_base import get_utcnow

from ..appointment_sms_reminder import AppointmentSmsReminder
from ..exceptions import AppointmentSmsReminderError


class TestAppointmentSmsReminder(TestCase):

    def setUp(self):
        self.remind_num_days_bfr_app = 4,
        self.appointment_date = get_utcnow().date()

    def test_reminder_date_app_date_today(self):
        """.Test that if appointment is today, reminder date returned is today.
        """
        reminder_date = AppointmentSmsReminder(
            appointment_date=self.appointment_date).reminder_date()
        self.assertEqual(reminder_date, self.appointment_date)

    def test_reminder_date_app_date_future(self):
        """.Test that if appointment is future, and the number of days a reminder
        has to be sent before an appointment is less than number of days from
        today to the appointment days.
        """
        appt_date = get_utcnow().date() + timedelta(21)
        reminder_date = AppointmentSmsReminder().reminder_date(
            appointment_date=appt_date)
        expected_reminder_date = get_utcnow().date() + timedelta(17)
        self.assertEqual(reminder_date, expected_reminder_date)

    def test_reminder_date_app_date_future2(self):
        """.Test that if appointment is future, and the number of days a reminder
        has to be sent before an appointment is more than number of days from
        today to the appointment days.
        """
        appt_date = get_utcnow().date() + timedelta(2)
        reminder_date = AppointmentSmsReminder().reminder_date(
            appointment_date=appt_date)
        expected_reminder_date = get_utcnow().date()
        self.assertEqual(reminder_date, expected_reminder_date)

    def test_reminder_date_app_date_past(self):
        """.Test that if appointment is future, and the number of days a reminder
        has to be sent before an appointment is more than number of days from
        today to the appointment days.
        """
        appt_date = get_utcnow().date() - timedelta(2)
        self.assertRaises(
            AppointmentSmsReminderError,
            AppointmentSmsReminder().reminder_date,
            appointment_date=appt_date)
