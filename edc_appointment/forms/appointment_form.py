from datetime import date

from django import forms
from django.contrib.admin.widgets import AdminRadioSelect, AdminRadioFieldRenderer
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.conf import settings

from edc_constants.constants import IN_PROGRESS, COMPLETE_APPT, KEYED, UNKEYED, NEW_APPT
from edc_meta_data.models import CrfMetaData, RequisitionMetaData

from ..models import Appointment


class AppointmentForm(forms.ModelForm):

    try:
        study_site = forms.ChoiceField(
            label='Study site',
            choices=settings.STUDY_SITES,
            help_text="",
            widget=AdminRadioSelect(renderer=AdminRadioFieldRenderer))
    except AttributeError:
        raise ImproperlyConfigured('Missing settings attribute STUDY_SITES.')

    class Meta:
        model = Appointment
        fields = '__all__'

    def clean(self):
        cleaned_data = super(AppointmentForm, self).clean()
        self.validate_time_point_status()
        self.validate_visit_instance()
        self.validate_complete_appt_date_cannot_be_future()
        self.validate_status_if_data_unkeyed()
        self.validate_status_if_data_keyed()
        self.validate_appt_status_in_progress()
        if cleaned_data['visit_instance'] == '':
            cleaned_data['visit_instance'] = '0'
        return cleaned_data

    def clean_appt_datetime(self):
        appt_datetime = self.cleaned_data['appt_datetime']
        if not appt_datetime:
            raise forms.ValidationError('Please provide the appointment date and time.')
        return appt_datetime

    def validate_time_point_status(self):
        try:
            self.instance.time_point_status_open_or_raise(exception_cls=forms.ValidationError)
        except AttributeError as e:
            if 'time_point_status_open_or_raise' not in str(e):
                raise AttributeError(e)

    def validate_visit_instance(self):
        cleaned_data = self.cleaned_data
        visit_instance = cleaned_data.get('visit_instance', '0')
        visit_instance = '0' if visit_instance == '' else visit_instance
        registered_subject = cleaned_data.get('registered_subject')
        visit_definition = self.get_visit_definition()
        if visit_instance != '0':
            previous = str(int(visit_instance) - 1)
            try:
                if not Appointment.objects.filter(
                        registered_subject=self.instance.registered_subject,
                        visit_definition=visit_definition,
                        visit_instance=previous).exists():
                    raise forms.ValidationError(
                        'Attempt to update appointment out of sequence. Got {}.'.format(visit_instance))
            except (AttributeError, ObjectDoesNotExist):
                if not Appointment.objects.filter(
                        registered_subject=registered_subject,
                        visit_definition=visit_definition,
                        visit_instance=previous).exists():
                    raise forms.ValidationError(
                        'Attempt to create appointment out of sequence. Got {}.'.format(visit_instance))

    def validate_complete_appt_date_cannot_be_future(self):
        cleaned_data = self.cleaned_data
        appt_status = cleaned_data.get("appt_status")
        appt_datetime = cleaned_data.get("appt_datetime")
        if appt_status == COMPLETE_APPT:
            try:
                t1 = appt_datetime.date() - date.today()
                if t1.days > 0:
                    raise forms.ValidationError(
                        'Appointment status is set to complete. '
                        'Appointment date cannot be a future date. '
                        'You wrote \'{}\'. Got {}'.format(appt_datetime, t1))
            except AttributeError as e:
                if 'date' not in str(e):
                    raise AttributeError(e)

    def validate_status_if_data_unkeyed(self):
        cleaned_data = self.cleaned_data
        appt_status = cleaned_data.get("appt_status")
        registered_subject = cleaned_data.get("registered_subject")
        visit_definition = self.get_visit_definition()
        if appt_status == COMPLETE_APPT:
            options = dict(
                appointment__registered_subject=registered_subject,
                appointment__visit_definition=visit_definition,
                entry_status=UNKEYED)
            if CrfMetaData.objects.filter(**options).exists():
                raise forms.ValidationError(
                    'Appointment is not \'complete\'. Some CRFs are still required.')
            if RequisitionMetaData.objects.filter(**options).exists():
                raise forms.ValidationError(
                    'Appointment is not \'complete\'. Some Requisitions are still required.')

    def validate_status_if_data_keyed(self):
        cleaned_data = self.cleaned_data
        appt_status = cleaned_data.get("appt_status")
        registered_subject = cleaned_data.get("registered_subject")
        visit_definition = self.get_visit_definition()
        if appt_status == NEW_APPT:
            options = dict(
                appointment__registered_subject=registered_subject,
                appointment__visit_definition=visit_definition,
                entry_status=KEYED)
            if CrfMetaData.objects.filter(**options).exists():
                raise forms.ValidationError(
                    'Appointment is not \'new\'. Some CRFs have been completed.')
            if RequisitionMetaData.objects.filter(**options).exists():
                raise forms.ValidationError(
                    'Appointment is not \'new\'. Some Requisitions have been completed.')

    def validate_appt_status_in_progress(self):
        cleaned_data = self.cleaned_data
        appt_status = cleaned_data.get("appt_status")
        registered_subject = cleaned_data.get("registered_subject")
        if appt_status == IN_PROGRESS:
            if Appointment.objects.filter(
                    registered_subject=registered_subject,
                    appt_status=IN_PROGRESS).exclude(
                    pk=self.instance.id).exists():
                raise forms.ValidationError(
                    'Another appointment is currently \'in progress\'. '
                    'Only one appointment may be in progress at a time. '
                    'Please resolve before continuing.')

    def get_visit_definition(self):
        cleaned_data = self.cleaned_data
        visit_definition = cleaned_data.get("visit_definition")
        if not visit_definition:
            try:
                visit_definition = self.instance.visit_definition
            except AttributeError:
                raise forms.ValidationError('Visit definition is required.')
        return visit_definition
