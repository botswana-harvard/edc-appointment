import pytz

from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA

from model_mommy import mommy

from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from edc_example.models import Appointment, SubjectConsent, Enrollment, RegisteredSubject, EnrollmentTwo

from .facility import Facility
from .models import Holiday
from decimal import Context
# from edc_visit_schedule.site_visit_schedules import site_visit_schedules


tz = pytz.timezone(settings.TIME_ZONE)


class TestAppointment(TestCase):

    def setUp(self):
        self.subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=timezone.now() - relativedelta(weeks=2))

    def test_appointments_creation(self):
        """Test if appointment triggering method creates appointments."""
        mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        self.assertEqual(Appointment.objects.all().count(), 4)

    def test_appointments_dates_mo(self):
        """Test appointment datetimes are chronological."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=timezone.now() - relativedelta(weeks=2),
            _quantity=7)

        for day in [MO, TU, WE, TH, FR, SA, SU]:
            subject_consent = SubjectConsent.objects.all()[day.weekday]
            mommy.make(
                Enrollment,
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=timezone.now() - relativedelta(weekday=day(-1)),
                schedule_name='schedule1')
            appt_datetimes = [obj.appt_datetime for obj in Appointment.objects.all().order_by('appt_datetime')]
            last = None
            for appt_datetime in appt_datetimes:
                if not last:
                    last = appt_datetime
                else:
                    self.assertGreater(appt_datetime, last)
                    last = appt_datetime

    def test_timepoint(self):
        """Assert timepoints are saved from the schedule correctly as Decimals and ordered by appt_datetime."""
        context = Context(prec=2)
        mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        self.assertEqual([obj.timepoint for obj in Appointment.objects.all().order_by('appt_datetime')],
                         [context.create_decimal(n) for n in range(0, 4)])

    def test_first_appointment_with_visit_schedule_and_schedule(self):
        """Asserts first appointment correctly selected if both visit_schedule_name and schedule_name
        provided."""
        mommy.make(
            EnrollmentTwo,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule2')
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier,
                visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
                schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1]).order_by('appt_datetime')[0],
            appointment)

    def test_first_appointment_with_visit_schedule(self):
        """Asserts first appointment correctly selected if just visit_schedule_name provided."""
        enrollment_two = mommy.make(
            EnrollmentTwo,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule2')
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0])
        self.assertEqual(
            appointment.schedule_name,
            enrollment_two._meta.visit_schedule_name.split('.')[-1])
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier,
                visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0]).order_by('appt_datetime')[0],
            appointment)

    def test_next_appointment(self):
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        appointment = Appointment.objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier).order_by('appt_datetime')[1],
            appointment)
        appointment = Appointment.objects.next_appointment(appointment=first_appointment)
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier).order_by('appt_datetime')[1],
            appointment)

    def test_next_appointment_after_last_returns_none(self):
        """Assert returns None if next after last appointment."""
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        last_appointment = Appointment.objects.last_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        self.assertEqual(Appointment.objects.next_appointment(appointment=last_appointment), None)

    def test_next_appointment_until_none(self):
        """Assert can walk from first to last appointment."""
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointments = Appointment.objects.filter(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1]).order_by('appt_datetime')
        first = Appointment.objects.first_appointment(appointment=appointments[0])
        appts = [first]
        for appointment in appointments:
            appts.append(Appointment.objects.next_appointment(appointment=appointment))
        self.assertIsNotNone(appts[0])
        self.assertEqual(appts[0], first)
        self.assertEqual(appts[-1], None)

    def test_previous_appointment1(self):
        """Assert returns None if relative to first appointment."""
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        self.assertEqual(Appointment.objects.previous_appointment(appointment=first_appointment), None)

    def test_previous_appointment2(self):
        """Assert returns previous appointment."""
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        next_appointment = Appointment.objects.next_appointment(appointment=first_appointment)
        self.assertEqual(Appointment.objects.previous_appointment(appointment=next_appointment), first_appointment)

    def test_next_and_previous_appointment3(self):
        """Assert accepts appointment or indiviual attrs."""
        enrollment = mommy.make(
            Enrollment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        first_appointment = Appointment.objects.first_appointment(
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        next_appointment = Appointment.objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=enrollment.subject_identifier,
            visit_schedule_name=enrollment._meta.visit_schedule_name.split('.')[0],
            schedule_name=enrollment._meta.visit_schedule_name.split('.')[-1])
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier).order_by('appt_datetime')[1],
            next_appointment)
        appointment = Appointment.objects.next_appointment(appointment=first_appointment)
        self.assertEqual(
            Appointment.objects.filter(
                subject_identifier=enrollment.subject_identifier).order_by('appt_datetime')[1],
            appointment)


class TestFacility(TestCase):

    def setUp(self):
        self.facility = Facility(name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        self.subject_identifier = '111111111'
        self.registered_subject = mommy.make(RegisteredSubject, subject_identifier=self.subject_identifier)
        self.subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            identity=self.subject_identifier,
            confirm_identity=self.subject_identifier,
            subject_identifier=self.subject_identifier,
            consent_datetime=timezone.now())

    def test_allowed_weekday(self):
        facility = Facility(name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        for suggested, available in [(MO, MO), (TU, TU), (WE, WE), (TH, TH), (FR, FR), (SA, MO), (SU, MO)]:
            dt = timezone.now() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(available.weekday, facility.available_datetime(dt, window_days=30).weekday())

    def test_allowed_weekday_limited(self):
        facility = Facility(name='clinic', days=[TU, TH], slots=[100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, TH), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = timezone.now() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(available.weekday, facility.available_datetime(dt, window_days=30).weekday())

    def test_allowed_weekday_limited2(self):
        facility = Facility(name='clinic', days=[TU, WE, TH], slots=[100, 100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, WE), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = timezone.now() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(available.weekday, facility.available_datetime(dt, window_days=30).weekday())

    def test_available_datetime(self):
        """Asserts finds available_datetime on first wednesday after suggested_date."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = timezone.now() + relativedelta(months=3)
        available_datetime = facility.available_datetime(suggested_date, window_days=30)
        self.assertEqual(available_datetime.weekday(), WE.weekday)

    def test_available_datetime_with_holiday(self):
        """Asserts finds available_datetime on first wednesday after holiday."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = timezone.now() + relativedelta(months=3)
        available_datetime1 = facility.available_datetime(suggested_date, window_days=30)
        self.assertEqual(available_datetime1.weekday(), WE.weekday)
        Holiday.objects.create(day=available_datetime1)
        available_datetime2 = facility.available_datetime(suggested_date, window_days=30)
        self.assertEqual(available_datetime2.weekday(), WE.weekday)
        self.assertGreater(available_datetime2, available_datetime1)