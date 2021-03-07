from datetime import timedelta

from django.apps import apps as django_apps

from edc_base.utils import get_utcnow
from edc_sms.classes import MessageSchedule

from .exceptions import AppointmentSmsReminderError


class AppointmentSmsReminder:

    message_schedule = MessageSchedule

    def __init__(
            self, appt_datetime=None, remind_num_days_bfr_app=None,
            subject_identifier=None, sms_message_data=None,
            sms_type=None, recipient_number=None):
        self.appt_datetime = appt_datetime
        self.remind_num_days_bfr_app = remind_num_days_bfr_app
        self.sms_message_data = sms_message_data
        self.subject_identifier = subject_identifier
        self.sms_type = sms_type
        self.recipient_number = recipient_number

        if not remind_num_days_bfr_app:
            app_config = django_apps.get_app_config('edc_appointment')
            self.remind_num_days_bfr_app = app_config.remind_num_days_bfr_app

    def reminder_date(self, appt_datetime=None):
        """Returns the date the sms should be sent.
        """
        appt_datetime = appt_datetime or self.appt_datetime
        if appt_datetime.date() == get_utcnow().date():
            return get_utcnow() + timedelta(hours=2, minutes=1)
        elif appt_datetime.date() > get_utcnow().date():
            delta = appt_datetime.date() - get_utcnow().date()
            if delta.days <= self.remind_num_days_bfr_app:
                return get_utcnow() + timedelta(hours=2, minutes=1)
            else:
                appt_datetime = appt_datetime + timedelta(hours=2, minutes=1)
                return appt_datetime - timedelta(
                    self.remind_num_days_bfr_app)
        elif appt_datetime.date() < get_utcnow().date():
            raise AppointmentSmsReminderError(
                'The appointment date can not be a past date. '
                f'Got {appt_datetime}')
        return None

    def schedule_or_send_sms_reminder(self, appt_reminder_date=None):
        """Sends or schedules an appointment sms reminder.
        """
        schedule_datetime = appt_reminder_date + timedelta(minutes=2)
        self.message_schedule().schedule_message(
            message_data=self.sms_message_data,
            recipient_number=self.recipient_number,
            subject_identifier=self.subject_identifier,
            sms_type='reminder', schedule_datetime=schedule_datetime)
