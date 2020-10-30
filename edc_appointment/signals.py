from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .appointment_sms_reminder import AppointmentSmsReminder


@receiver(post_save, weak=False,
          dispatch_uid="create_appointments_on_post_save")
def create_appointments_on_post_save(sender, instance, raw,
                                     created, using, **kwargs):
    if not raw and not kwargs.get('update_fields'):
        try:
            instance.create_appointments()
        except AttributeError as e:
            if 'create_appointments' not in str(e):
                raise


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus in appointment if the
    field is empty.
    """
    if not raw:
        try:
            if not instance.time_point_status:
                instance.time_point_status
                instance.save(update_fields=['time_point_status'])
        except AttributeError as e:
            if 'time_point_status' not in str(e):
                raise


@receiver(post_delete, weak=False,
          dispatch_uid="delete_appointments_on_post_delete")
def delete_appointments_on_post_delete(sender, instance, using, **kwargs):
    try:
        instance.delete_unused_appointments()
    except AttributeError:
        pass


def appointment_reminder_model_cls():
    app_config = django_apps.get_app_config('edc_appointment')
    model = app_config.appt_reminder_model
    return django_apps.get_model(model)


@receiver(post_save, weak=True, sender=appointment_reminder_model_cls(),
          dispatch_uid='appointment_reminder_on_post_save')
def appointment_reminder_on_post_save(sender, instance, raw, created, using, **kwargs):
    """
    Schedule an sms reminder when appointment is created.
    """
    if not raw:
        if created:
            # Appointment sms reminder
            app_config = django_apps.get_app_config('edc_appointment')
            send_sms_reminders = app_config.send_sms_reminders

            if send_sms_reminders:
                try:
                    appt_datetime = instance.appt_datetime.strftime(
                        "%B+%d,+%Y,+%H:%M:%S")
                except AttributeError:
                    pass
                else:
                    edc_sms_app_config = django_apps.get_app_config('edc_sms')
                    consent_mdl_cls = django_apps.get_model(
                        edc_sms_app_config.consent_model)
                    consent = consent_mdl_cls.objects.filter(
                        subject_identifier=instance.subject_identifier)
                    if consent:
                        consent = consent[0]
                    sms_message_data = (
                        f'Dear+participant+Reminder+for+an+appointment+on+{appt_datetime}')
                    appt_sms_reminder = AppointmentSmsReminder(
                        subject_identifier=instance.subject_identifier,
                        appt_datetime=instance.appt_datetime,
                        sms_message_data=sms_message_data,
                        recipient_number=consent.recipient_number)
                    appt_reminder_date = instance.appt_datetime
                    appt_sms_reminder.schedule_or_send_sms_reminder(
                        appt_reminder_date=appt_reminder_date)
