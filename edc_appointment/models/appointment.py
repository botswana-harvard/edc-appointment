from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin
from edc_calender.models import UpdatesOrCreatesCalenderEventModelMixin

from ..managers import AppointmentManager
from ..model_mixins import AppointmentModelMixin


class Appointment(AppointmentModelMixin, UpdatesOrCreatesCalenderEventModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = AppointmentManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name,
                self.visit_code,
                self.visit_code_sequence)
    natural_key.dependencies = ['sites.Site']

    @property
    def event_options(self):
        """Returns the dict of the following attrs
        `title` `description` `start_time`  `end_time`.
        """
        return {
            'description': self.appt_reason,
            'start_time': self.appt_datetime,
            'end_time': self.appt_datetime,}

    class Meta(AppointmentModelMixin.Meta):
        pass
