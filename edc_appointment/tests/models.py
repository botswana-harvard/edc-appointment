from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins import OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin
from uuid import uuid4
from edc_sms.models import SubjectConsentRecipient

from ..models import Appointment


class MyModel(VisitModelMixin, BaseUuidModel):
    pass


class SubjectConsent(NonUniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     SubjectConsentRecipient,
                     BaseUuidModel):

    consent_datetime = models.DateTimeField(
        default=get_utcnow)

    first_name = models.CharField(
        blank=True,
        null=True,
        max_length=100)

    last_name = models.CharField(
        blank=True,
        null=True,
        max_length=100)

    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_identifier = models.UUIDField(default=uuid4)

    @property
    def recipient_number(self):
        """Return a mobile number.

        Override to return a mobile number format: 26771111111.
        """
        return '26771522602'

    @property
    def registration_unique_field(self):
        return 'subject_identifier'


class OnScheduleOne(OnScheduleModelMixin, BaseUuidModel):

    pass


class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):

    pass


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)


class Locator(BaseUuidModel):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        null=True, blank=True,
        max_length=100)

    subject_cell = models.CharField(
        verbose_name='Cell number',
        max_length=100,
        blank=True,
        null=True)

    subject_cell_alt = models.CharField(
        verbose_name='Cell number (alternate)',
        max_length=100,
        blank=True,
        null=True)
