from datetime import timedelta

from django.apps import apps as django_apps

from edc_base.utils import get_utcnow

from .exceptions import AppointmentSmsReminderError


class AppointmentSmsReminder:

    def __init__(self, appointment_date=None, remind_num_days_bfr_app=None):
        self.appointment_date = appointment_date
        self.remind_num_days_bfr_app = remind_num_days_bfr_app

        if not remind_num_days_bfr_app:
            app_config = django_apps.get_app_config('edc_appointment')
            self.remind_num_days_bfr_app = app_config.remind_num_days_bfr_app

    def reminder_date(self, appointment_date=None):
        """Returns the date the sms should be sent.
        """
        appointment_date = appointment_date or self.appointment_date
        if appointment_date == get_utcnow().date():
            return appointment_date
        elif appointment_date > get_utcnow().date():
            delta = appointment_date - get_utcnow().date()
            if delta.days <= self.remind_num_days_bfr_app:
                return get_utcnow().date()
            else:
                return appointment_date - timedelta(
                    self.remind_num_days_bfr_app)
        elif appointment_date < get_utcnow().date():
            raise AppointmentSmsReminderError(
                'The appointment date can not be a past date. '
                f'Got {appointment_date}')
        return None
