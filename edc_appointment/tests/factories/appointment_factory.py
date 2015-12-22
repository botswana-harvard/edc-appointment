import factory

from datetime import datetime

from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.core.bhp_variables.tests.factories import StudySiteFactory
from edc.subject.registration.tests.factories import RegisteredSubjectFactory
from edc_visit_schedule.tests.factories import VisitDefinitionFactory

from edc_appointment.models import Appointment


class AppointmentFactory(BaseUuidModelFactory):

    class Meta:
        model = Appointment

    registered_subject = factory.SubFactory(RegisteredSubjectFactory)
    appt_datetime = datetime.today()
    best_appt_datetime = datetime.today()
    appt_close_datetime = datetime.today()
    study_site = factory.SubFactory(StudySiteFactory)
    visit_definition = factory.SubFactory(VisitDefinitionFactory)
    visit_instance = '0'
