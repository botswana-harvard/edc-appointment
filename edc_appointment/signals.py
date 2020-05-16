from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


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

    #         app_config = django_apps.get_app_config('edc_appointment')
    #         send_sms_reminders = app_config.send_sms_reminders
    #         sms_remind_num_days_before_app = app_config.sms_remind_num_days_before_app
    #         if send_sms_reminders:
    #             sms_remind_num_days_before_app


@receiver(post_delete, weak=False,
          dispatch_uid="delete_appointments_on_post_delete")
def delete_appointments_on_post_delete(sender, instance, using, **kwargs):
    try:
        instance.delete_unused_appointments()
    except AttributeError:
        pass
