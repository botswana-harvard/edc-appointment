from uuid import uuid4

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models, transaction

from simple_history.models import HistoricalRecords as AuditTrail

from edc_constants.constants import COMPLETE_APPT, NEW_APPT, CANCELLED, INCOMPLETE, UNKEYED, IN_PROGRESS
from edc_visit_schedule.models import VisitDefinition, Schedule

from .appointment_date_helper import AppointmentDateHelper
from .choices import APPT_TYPE, APPT_STATUS
from .exceptions import AppointmentStatusError, AppointmentCreateError
from .window_period_helper import WindowPeriodHelper


class AppointmentMixin(models.Model):

    """ Model Mixin to add methods to create appointments.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments.

    """
    @property
    def appointment_app_config(self):
        return django_apps.get_app_config('edc_appointment')

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').appointment_model

    def pre_prepare_appointments(self, using):
        """Users may override to add functionality before creating appointments."""
        return None

    def post_prepare_appointments(self, appointments, using):
        """Users may override to add functionality after creating appointments."""
        return None

    def prepare_appointments(self, using):
        """Creates all appointments linked to this instance.

        Calls :func:`pre_prepare_appointments` and :func:`post_prepare_appointments`
        """
        self.pre_prepare_appointments(using)
        appointments = self.create_all(using=using)
        self.post_prepare_appointments(appointments, using)
        return appointments

    def create_all(self, base_appt_datetime=None, using=None,
                   visit_definitions=None, dashboard_type=None):
        """Creates appointments for a registered subject based on a list
        of visit definitions for the given membership form instance.

            1. this is called from a post-save signal
            2. RegisteredSubject instance is expected to exist at this point
            3. Only create for visit_instance = '0'
            4. If appointment exists, just update the appt_datetime

            visit_definition contains the schedule group which contains the membership form
        """
        appointments = []
        appointment_identifier = str(uuid4())
        for visit_definition in self.visit_definitions_for_schedule(self._meta.model_name):
            appointment = self.update_or_create_appointment(
                base_appt_datetime or self.get_registration_datetime(),
                visit_definition,
                self.appointment_app_config.default_appt_type,
                dashboard_type,
                appointment_identifier,
                using)
            appointments.append(appointment)
        return appointments

    def update_or_create_appointment(self, registration_datetime, visit_definition,
                                     default_appt_type, dashboard_type, appointment_identifier, using):
        """Updates or creates an appointment for this subject for the visit_definition."""
        appt_datetime = self.new_appointment_appt_datetime(
            appointment_identifier=appointment_identifier,
            registration_datetime=registration_datetime,
            visit_definition=visit_definition)
        try:
            appointment = self.appointment_model.objects.using(using).get(
                appointment_identifier=appointment_identifier,
                visit_definition=visit_definition,
                visit_instance='0')
            td = appointment.best_appt_datetime - appt_datetime
            if td.days == 0 and abs(td.seconds) > 59:
                # the calculated appointment date does not match
                # the best_appt_datetime (not within 59 seconds)
                # which means you changed the date on the membership form and now
                # need to correct the best_appt_datetime
                appointment.appt_datetime = appt_datetime
                appointment.best_appt_datetime = appt_datetime
                appointment.save(using, update_fields=['appt_datetime', 'best_appt_datetime'])
        except self.appointment_model.DoesNotExist:
            appointment = self.appointment_model.objects.using(using).create(
                appointment_identifier=appointment_identifier,
                visit_definition=visit_definition,
                visit_instance='0',
                appt_datetime=appt_datetime,
                timepoint_datetime=appt_datetime,
                dashboard_type=dashboard_type,
                appt_type=default_appt_type)
        return appointment

    def visit_definitions_for_schedule(self, model_name):
        """Returns a visit_definition queryset for this membership form's schedule."""
        # VisitDefinition = get_model('edc_visit_schedule', 'VisitDefinition')
        schedule = self.schedule(model_name)
        visit_definitions = VisitDefinition.objects.filter(
            schedule=schedule).order_by('time_point')
        if not visit_definitions:
            raise AppointmentCreateError(
                'No visit_definitions found for membership form class {0} '
                'in schedule group {1}. Expected at least one visit '
                'definition to be associated with schedule group {1}.'.format(
                    model_name, schedule))
        return visit_definitions

    def schedule(self, model_name):
        """Returns the schedule for this membership_form."""
        try:
            schedule = Schedule.objects.get(
                membership_form__content_type_map__model=model_name)
        except Schedule.DoesNotExist:
            raise Schedule.DoesNotExist(
                'Cannot prepare appointments for membership form. '
                'Membership form \'{}\' not found in Schedule. '
                'See the visit schedule configuration.'.format(model_name))
        return schedule

    def new_appointment_appt_datetime(
            self, registered_subject, registration_datetime, visit_definition):
        """Calculates and returns the appointment date for new appointments."""
        appointment_date_helper = AppointmentDateHelper(self.appointment_model)
        if visit_definition.time_point == 0:
            appt_datetime = appointment_date_helper.get_best_datetime(
                registration_datetime, registered_subject.study_site)
        else:
            appt_datetime = appointment_date_helper.get_relative_datetime(
                registration_datetime, visit_definition)
        return appt_datetime

    class Meta:
        abstract = True


class AppointmentModelMixin(models.Model):
    """Tracks appointments for a registered subject's visit.

        Only one appointment per subject visit_definition+visit_instance.
        Attribute 'visit_instance' should be populated by the system.
    """

    visit_definition = models.ForeignKey(
        VisitDefinition,
        related_name='+',
        verbose_name="Visit",
        help_text=("For tracking within the window period of a visit, use the decimal convention. "
                   "Format is NNNN.N. e.g 1000.0, 1000.1, 1000.2, etc)"))

    #  This identifier is common across a subject's appointment
    appointment_identifier = models.CharField(
        verbose_name="Identifier",
        max_length=50,
        blank=True,
        db_index=True,
        unique=True)

    best_appt_datetime = models.DateTimeField(null=True, editable=False)

    appt_close_datetime = models.DateTimeField(null=True, editable=False)

    visit_instance = models.CharField(
        max_length=1,
        verbose_name=("Instance"),
        validators=[RegexValidator(r'[0-9]', 'Must be a number from 0-9')],
        default='0',
        null=True,
        blank=True,
        db_index=True,
        help_text=("A decimal to represent an additional report to be included with the original "
                   "visit report. (NNNN.0)"))
    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="",
        db_index=True)

    # this is the original calculated appointment datetime
    # which the user cannot change
    timepoint_datetime = models.DateTimeField(
        verbose_name=("Timepoint date and time"),
        help_text="calculated appointment datetime. Do not change",
        null=True,
        editable=False)

#     time_point_status = models.ForeignKey(TimePointStatus, null=True, blank=True)

    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default=NEW_APPT,
        db_index=True)

    appt_reason = models.CharField(
        verbose_name=("Reason for appointment"),
        max_length=25,
        help_text=("Reason for appointment"),
        blank=True)

    contact_tel = models.CharField(
        verbose_name=("Contact Tel"),
        max_length=250,
        blank=True)

    comment = models.CharField(
        "Comment",
        max_length=250,
        blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    contact_count = models.IntegerField(default=0, editable=False)

    dashboard_type = models.CharField(
        max_length=25,
        editable=False,
        null=True,
        blank=True,
        db_index=True,
        help_text='hold dashboard_type variable, set by dashboard')

    appt_type = models.CharField(
        verbose_name='Appointment type',
        choices=APPT_TYPE,
        default='clinic',
        max_length=20,
        help_text=(
            'Default for subject may be edited in admin under section bhp_subject. '
            'See Subject Configuration.'))

    # objects = AppointmentManager()

    history = AuditTrail()

    def __unicode__(self):
        return "{0} {1}".format(
            self.visit_definition.code, self.visit_instance)

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not self.subject_registration_instance():
            raise ValidationError("Subject registration instance can not be null.")
        if not kwargs.get('update_fields'):
            self.validate_visit_instance()
            if self.id:
                self.time_point_status_open_or_raise()
            if self.visit_instance == '0':
                self.appt_datetime, self.best_appt_datetime = self.validate_appt_datetime()
            else:
                self.appt_datetime, self.best_appt_datetime = self.validate_continuation_appt_datetime()
            self.check_window_period()
            self.appt_status = self.get_appt_status(using)
        super(AppointmentModelMixin, self).save(*args, **kwargs)

#     def natural_key(self):
#         """Returns a natural key."""
#         return (self.visit_instance, ) + self.visit_definition.natural_key() + self.registered_subject.natural_key()
#     natural_key.dependencies = ['edc_registration.registeredsubject', 'edc_visit_schedule.visitdefinition']

    def get_appt_status(self, using):
        """Returns the appt_status by checking the meta data entry status for all required CRFs and requisitions.
        """
        from edc_meta_data.helpers import CrfMetaDataHelper
        appt_status = self.appt_status
        visit_model = self.visit_definition.visit_tracking_content_type_map.model_class()
        try:
            visit_instance = visit_model.objects.get(appointment=self)
            crf_meta_data_helper = CrfMetaDataHelper(self, visit_instance)
            if not crf_meta_data_helper.show_entries():
                appt_status = COMPLETE_APPT
            else:
                if appt_status in [COMPLETE_APPT, INCOMPLETE]:
                    appt_status = INCOMPLETE if self.unkeyed_forms() else COMPLETE_APPT
                elif appt_status in [NEW_APPT, CANCELLED, IN_PROGRESS]:
                    appt_status = IN_PROGRESS
                    self.update_others_as_not_in_progress(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(self.appt_status))
        except visit_model.DoesNotExist:
            if self.appt_status not in [NEW_APPT, CANCELLED]:
                appt_status = NEW_APPT
        return appt_status

    def validate_visit_instance(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        visit_instance = self.visit_instance or '0'
        if self.visit_instance != '0':
            previous = str(int(visit_instance) - 1)
            try:
                appointment = self.__class__.objects.get(
                    appointment_identifier=self.appointment_identifier,
                    visit_definition=self.visit_definition,
                    visit_instance=previous)
                if appointment.id == self.id:
                    raise self.__class__.DoesNotExist
            except self.__class__.DoesNotExist:
                raise exception_cls(
                    'Attempt to create or update appointment instance out of sequence. Got \'{}.{}\'.'.format(
                        self.visit_definition.code, visit_instance))

    def update_others_as_not_in_progress(self, using):
        """Updates other appointments for this registered subject to not be IN_PROGRESS.

        Only one appointment can be "in_progress", so look for any others in progress and change
        to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)"""

        for appointment in self.__class__.objects.filter(
                appointment_identifier=self.appointment_identifier,
                appt_status=IN_PROGRESS).exclude(
                    pk=self.pk):
            with transaction.atomic(using):
                if self.unkeyed_forms():
                    if appointment.appt_status != INCOMPLETE:
                        appointment.appt_status = INCOMPLETE
                        appointment.save(using, update_fields=['appt_status'])
                else:
                    if appointment.appt_status != COMPLETE_APPT:
                        appointment.appt_status = COMPLETE_APPT
                        appointment.save(using, update_fields=['appt_status'])

    def unkeyed_forms(self):
        if self.unkeyed_crfs() or self.unkeyed_requisitions():
            return True
        return False

    def subject_registration_instance(self):
        """Returns the subject registration instance.

        Overide this method at the APPOINTMENT_MODEL"""
        return None

    def unkeyed_crfs(self):
        from edc_meta_data.helpers import CrfMetaDataHelper
        return CrfMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def unkeyed_requisitions(self):
        from edc_meta_data.helpers import RequisitionMetaDataHelper
        return RequisitionMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

#     def time_point_status_open_or_raise(self, exception_cls=None):
#         """Checks the timepoint status and prevents edits to the model if
#         time_point_status_status == closed."""
#         exception_cls = exception_cls or ValidationError
#         try:
#             if self.time_point_status.status == CLOSED:
#                 raise ValidationError('Data entry for this time point is closed. See TimePointStatus.')
#         except AttributeError:
#             pass
#         except TimePointStatus.DoesNotExist:
#             self.time_point_status = TimePointStatus.objects.create(
#                 visit_code=self.visit_definition.code,
#                 appointment_identifier=self.appointment_identifier)  # TODO quesry with someything that uniquely idetifier all other subject's appointments

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None'
         will raise an exception."""
        if not exception_cls:
            exception_cls = ValidationError
        appointment_date_helper = AppointmentDateHelper(self.__class__)
        if not self.id:
            appt_datetime = appointment_date_helper.get_best_datetime(
                self.appt_datetime, self.subject_registration_instance.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = appointment_date_helper.change_datetime(
                self.best_appt_datetime, self.appt_datetime,
                self.subject_registration_instance.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        base_appointment = self.__class__.objects.get(
            appointment_identifier=self.appointment_identifier,
            visit_definition=self.visit_definition,
            visit_instance='0')
        if self.visit_instance != '0' and (self.appt_datetime - base_appointment.appt_datetime).days < 1:
            raise exception_cls(
                'Appointment date must be a future date relative to the '
                'base appointment. Got {} not greater than {} at {}.0.'.format(
                    self.appt_datetime.strftime('%Y-%m-%d'),
                    base_appointment.appt_datetime.strftime('%Y-%m-%d'),
                    self.visit_definition.code))
        return self.appt_datetime, base_appointment.best_appt_datetime

    def check_window_period(self, exception_cls=None):
        """Confirms appointment date is in the accepted window period."""
        if not exception_cls:
            exception_cls = ValidationError
        if self.id and self.visit_instance == '0':
            window_period = WindowPeriodHelper(
                self.visit_definition, self.appt_datetime, self.best_appt_datetime)
            if not window_period.check_datetime():
                raise exception_cls(window_period.error_message)

#     def dashboard(self):
#         """Returns a hyperink for the Admin page."""
#         ret = None
#         if settings.APP_NAME == 'cancer':
#                 if self.appointment_identifier:
#                     url = reverse('subject_dashboard_url',
#                                   kwargs={'dashboard_type': self.registered_subject.subject_type.lower(),
#                                           'dashboard_model': 'appointment',
#                                           'dashboard_id': self.pk,
#                                           'show': 'appointments'})
#                     ret = """<a href="{url}" />dashboard</a>""".format(url=url)
#         if self.appt_status == APPT_STATUS[0][0]:
#             if settings.APP_NAME != 'cancer':
#                 return NEW_APPT
#         else:
#             if self.registered_subject:
#                 if self.registered_subject.subject_identifier:
#                     url = reverse('subject_dashboard_url',
#                                   kwargs={'dashboard_type': self.registered_subject.subject_type.lower(),
#                                           'dashboard_model': 'appointment',
#                                           'dashboard_id': self.pk,
#                                           'show': 'appointments'})
#                     ret = """<a href="{url}" />dashboard</a>""".format(url=url)
#         return ret
#     dashboard.allow_tags = True

    def time_point(self):
        url = reverse('admin:edc_appointment_timepointstatus_changelist')
        return """<a href="{url}?appointment_identifier={appointment_identifier}" />time_point</a>""".format(
            url=url, appointment_identifier=self.appointment_identifier)
    time_point.allow_tags = True

    def get_report_datetime(self):
        """Returns the appointment datetime as the report_datetime."""
        return self.appt_datetime

    def is_new_appointment(self):
        """Returns True if this is a New appointment and confirms choices
        tuple has \'new\'; as a option."""
        if NEW_APPT not in [s[0] for s in APPT_STATUS]:
            raise TypeError(
                'Expected (\'new\', \'New\') as one tuple in the choices tuple '
                'APPT_STATUS. Got {0}'.format(APPT_STATUS))
        retval = False
        if self.appt_status == NEW_APPT:
            retval = True
        return retval

    @property
    def complete(self):
        """Returns True if the appointment status is COMPLETE_APPT."""
        return self.appt_status == COMPLETE_APPT

    class Meta:
        abstract = True


class RequiresAppointmentMixin(models.Model):

    APPOINTMENT_MODEL = None

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if not self.subject_registration_instance():
            raise ValidationError("Subject registration instance can not be null.")
        if not kwargs.get('update_fields'):
            self.validate_visit_instance()
            if self.id:
                self.time_point_status_open_or_raise()
            if self.visit_instance == '0':
                self.appt_datetime, self.best_appt_datetime = self.validate_appt_datetime()
            else:
                self.appt_datetime, self.best_appt_datetime = self.validate_continuation_appt_datetime()
            self.check_window_period()
            self.appt_status = self.get_appt_status(using)
        super(RequiresAppointmentMixin, self).save(*args, **kwargs)

#     def natural_key(self):
#         """Returns a natural key."""
#         return (self.visit_instance, ) + self.visit_definition.natural_key() + self.registered_subject.natural_key()
#     natural_key.dependencies = ['edc_registration.registeredsubject', 'edc_visit_schedule.visitdefinition']

    def get_appt_status(self, using):
        """Returns the appt_status by checking the meta data entry status for all required CRFs and requisitions.
        """
        from edc_meta_data.helpers import CrfMetaDataHelper
        appt_status = self.appt_status
        visit_model = self.visit_definition.visit_tracking_content_type_map.model_class()
        try:
            visit_instance = visit_model.objects.get(appointment=self)
            crf_meta_data_helper = CrfMetaDataHelper(self, visit_instance)
            if not crf_meta_data_helper.show_entries():
                appt_status = COMPLETE_APPT
            else:
                if appt_status in [COMPLETE_APPT, INCOMPLETE]:
                    appt_status = INCOMPLETE if self.unkeyed_forms() else COMPLETE_APPT
                elif appt_status in [NEW_APPT, CANCELLED, IN_PROGRESS]:
                    appt_status = IN_PROGRESS
                    self.update_others_as_not_in_progress(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(self.appt_status))
        except visit_model.DoesNotExist:
            if self.appt_status not in [NEW_APPT, CANCELLED]:
                appt_status = NEW_APPT
        return appt_status

    def validate_visit_instance(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        visit_instance = self.visit_instance or '0'
        if self.visit_instance != '0':
            previous = str(int(visit_instance) - 1)
            try:
                appointment = self.APPOINTMENT_MODEL.objects.get(
                    appointment_identifier=self.appointment_identifier,
                    visit_definition=self.visit_definition,
                    visit_instance=previous)
                if appointment.id == self.id:
                    raise self.APPOINTMENT_MODEL.DoesNotExist
            except self.APPOINTMENT_MODEL.DoesNotExist:
                raise exception_cls(
                    'Attempt to create or update appointment instance out of sequence. Got \'{}.{}\'.'.format(
                        self.visit_definition.code, visit_instance))

    def update_others_as_not_in_progress(self, using):
        """Updates other appointments for this registered subject to not be IN_PROGRESS.

        Only one appointment can be "in_progress", so look for any others in progress and change
        to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)"""

        for appointment in self.APPOINTMENT_MODEL.objects.filter(
                appointment_identifier=self.appointment_identifier,
                appt_status=IN_PROGRESS).exclude(
                    pk=self.pk):
            with transaction.atomic(using):
                if self.unkeyed_forms():
                    if appointment.appt_status != INCOMPLETE:
                        appointment.appt_status = INCOMPLETE
                        appointment.save(using, update_fields=['appt_status'])
                else:
                    if appointment.appt_status != COMPLETE_APPT:
                        appointment.appt_status = COMPLETE_APPT
                        appointment.save(using, update_fields=['appt_status'])

    def unkeyed_forms(self):
        if self.unkeyed_crfs() or self.unkeyed_requisitions():
            return True
        return False

    def subject_registration_instance(self):
        """Returns the subject registration instance.

        Overide this method at the APPOINTMENT_MODEL"""
        return None

    def unkeyed_crfs(self):
        from edc_meta_data.helpers import CrfMetaDataHelper
        return CrfMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

    def unkeyed_requisitions(self):
        from edc_meta_data.helpers import RequisitionMetaDataHelper
        return RequisitionMetaDataHelper(self).get_meta_data(entry_status=UNKEYED)

#     def time_point_status_open_or_raise(self, exception_cls=None):
#         """Checks the timepoint status and prevents edits to the model if
#         time_point_status_status == closed."""
#         exception_cls = exception_cls or ValidationError
#         try:
#             if self.time_point_status.status == CLOSED:
#                 raise ValidationError('Data entry for this time point is closed. See TimePointStatus.')
#         except AttributeError:
#             pass
#         except TimePointStatus.DoesNotExist:
#             self.time_point_status = TimePointStatus.objects.create(
#                 visit_code=self.visit_definition.code,
#                 appointment_identifier=self.appointment_identifier)  # TODO quesry with someything that uniquely idetifier all other subject's appointments

    def validate_appt_datetime(self, exception_cls=None):
        """Returns the appt_datetime, possibly adjusted, and the best_appt_datetime,
        the calculated ideal timepoint datetime.

        .. note:: best_appt_datetime is not editable by the user. If 'None'
         will raise an exception."""
        if not exception_cls:
            exception_cls = ValidationError
        appointment_date_helper = AppointmentDateHelper(self.APPOINTMENT_MODEL)
        if not self.id:
            appt_datetime = appointment_date_helper.get_best_datetime(
                self.appt_datetime, self.subject_registration_instance.study_site)
            best_appt_datetime = self.appt_datetime
        else:
            if not self.best_appt_datetime:
                # did you update best_appt_datetime for existing instances since the migration?
                raise exception_cls(
                    'Appointment instance attribute \'best_appt_datetime\' cannot be null on change.')
            appt_datetime = appointment_date_helper.change_datetime(
                self.best_appt_datetime, self.appt_datetime,
                self.subject_registration_instance.study_site, self.visit_definition)
            best_appt_datetime = self.best_appt_datetime
        return appt_datetime, best_appt_datetime

    def validate_continuation_appt_datetime(self, exception_cls=None):
        exception_cls = exception_cls or ValidationError
        base_appointment = self.APPOINTMENT_MODEL.objects.get(
            appointment_identifier=self.appointment_identifier,
            visit_definition=self.visit_definition,
            visit_instance='0')
        if self.visit_instance != '0' and (self.appt_datetime - base_appointment.appt_datetime).days < 1:
            raise exception_cls(
                'Appointment date must be a future date relative to the '
                'base appointment. Got {} not greater than {} at {}.0.'.format(
                    self.appt_datetime.strftime('%Y-%m-%d'),
                    base_appointment.appt_datetime.strftime('%Y-%m-%d'),
                    self.visit_definition.code))
        return self.appt_datetime, base_appointment.best_appt_datetime

    def check_window_period(self, exception_cls=None):
        """Confirms appointment date is in the accepted window period."""
        if not exception_cls:
            exception_cls = ValidationError
        if self.id and self.visit_instance == '0':
            window_period = WindowPeriodHelper(
                self.visit_definition, self.appt_datetime, self.best_appt_datetime)
            if not window_period.check_datetime():
                raise exception_cls(window_period.error_message)

    def time_point(self):
        url = reverse('admin:edc_appointment_timepointstatus_changelist')
        return """<a href="{url}?appointment_identifier={appointment_identifier}" />time_point</a>""".format(
            url=url, appointment_identifier=self.appointment_identifier)
    time_point.allow_tags = True

    def get_report_datetime(self):
        """Returns the appointment datetime as the report_datetime."""
        return self.appt_datetime

    def is_new_appointment(self):
        """Returns True if this is a New appointment and confirms choices
        tuple has \'new\'; as a option."""
        if NEW_APPT not in [s[0] for s in APPT_STATUS]:
            raise TypeError(
                'Expected (\'new\', \'New\') as one tuple in the choices tuple '
                'APPT_STATUS. Got {0}'.format(APPT_STATUS))
        retval = False
        if self.appt_status == NEW_APPT:
            retval = True
        return retval

    @property
    def complete(self):
        """Returns True if the appointment status is COMPLETE_APPT."""
        return self.appt_status == COMPLETE_APPT

    class Meta:
        abstract = True
