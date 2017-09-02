from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse

from edc_model_wrapper import ModelWrapper


class AppointmentModelWrapper(ModelWrapper):

    model = None  # django_apps.get_app_config('edc_appointment').model
    visit_model_wrapper_cls = None

    def get_appt_status_display(self):
        return self.object.get_appt_status_display()

    @property
    def title(self):
        return self.object.title

    @property
    def wrapped_visit(self):
        """Returns a wrapped persistent or non-persistent visit instance.
        """
        try:
            model_obj = self.object.subjectvisit
        except ObjectDoesNotExist:
            visit_model = django_apps.get_model(
                *self.visit_model_wrapper_cls.model.split('.'))
            model_obj = visit_model(
                appointment=self.object,
                subject_identifier=self.subject_identifier,)
        return self.visit_model_wrapper_cls(model_obj=model_obj)

    @property
    def forms_url(self):
        """Returns a reversed URL to show forms for this appointment/visit.

        This is standard for edc_dashboard.
        """
        kwargs = dict(
            subject_identifier=self.subject_identifier,
            appointment=self.object.id)
        return reverse(self.dashboard_url_name, kwargs=kwargs)
