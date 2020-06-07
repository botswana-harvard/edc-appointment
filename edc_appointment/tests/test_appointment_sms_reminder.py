from datetime import timedelta

from django.test import TestCase

from edc_base.utils import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..appointment_sms_reminder import AppointmentSmsReminder
from ..exceptions import AppointmentSmsReminderError
from ..models import Appointment
from .helper import Helper
from .models import Locator, SubjectConsent
from .visit_schedule import visit_schedule1, visit_schedule2


class TestAppointmentSmsReminder(TestCase):

    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.remind_num_days_bfr_app = 4,
        self.appt_datetime = get_utcnow()
        self.subject_identifier = '12345'
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=self.appt_datetime)

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow())
        self.locator = Locator.objects.create(
            subject_identifier=self.subject_identifier,
            subject_cell='26771522602',
            subject_cell_alt='26771883071')

    def test_reminder_date_app_date_today(self):
        """.Test that if appointment is today, reminder date returned is today.
        """
        reminder_date = AppointmentSmsReminder(
            appt_datetime=self.appt_datetime).reminder_date()
        self.assertEqual(reminder_date.date(), self.appt_datetime.date())

    def test_reminder_date_app_date_future(self):
        """.Test that if appointment is future, and the number of days a reminder
        has to be sent before an appointment is less than number of days from
        today to the appointment days.
        """
        appt_datetime = get_utcnow() + timedelta(21)
        reminder_date = AppointmentSmsReminder().reminder_date(
            appt_datetime=appt_datetime)
        expected_reminder_date = get_utcnow().date() + timedelta(17)
        self.assertEqual(reminder_date.date(), expected_reminder_date)

    def test_reminder_date_app_date_future2(self):
        """.Test that if appointment is future, and the number of days a reminder
        has to be sent before an appointment is more than number of days from
        today to the appointment days.
        """
        appt_datetime = get_utcnow() + timedelta(2)
        reminder_date = AppointmentSmsReminder().reminder_date(
            appt_datetime=appt_datetime)
        expected_reminder_date = get_utcnow().date()
        self.assertEqual(reminder_date.date(), expected_reminder_date)

    def test_reminder_date_app_date_past(self):
        """.Test that if appointment is future, and the number of days a reminder
        has to be sent before an appointment is more than number of days from
        today to the appointment days.
        """
        appt_datetime = get_utcnow() - timedelta(2)
        self.assertRaises(
            AppointmentSmsReminderError,
            AppointmentSmsReminder().reminder_date,
            appt_datetime=appt_datetime)

    def test_send_appt_reminder(self):
        """Test if an appointment sms reminder is sent.
        """
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)
