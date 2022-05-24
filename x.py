        base_appt_datetime = datetime(2017, 1, 7)  # noqa
        self.assertTrue(weekday(base_appt_datetime.weekday()), SA)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime, subject_identifier="123456"
        )
        self.assertTrue(weekday(appt_datetimes[0].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TU)

        base_appt_datetime = datetime(2017, 1, 8)
        self.assertTrue(weekday(base_appt_datetime.weekday()), SU)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime, subject_identifier="1234567"
        )
        self.assertTrue(weekday(appt_datetimes[0].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TU)

        base_appt_datetime = datetime(2017, 1, 9)
        self.assertTrue(weekday(base_appt_datetime.weekday()), MO)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime, subject_identifier="12345678"
        )
        self.assertTrue(weekday(appt_datetimes[0].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TU)

        base_appt_datetime = datetime(2017, 1, 10)
        self.assertTrue(weekday(base_appt_datetime.weekday()), TU)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime, subject_identifier="123456789"
        )
        self.assertTrue(weekday(appt_datetimes[0].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TU)

        base_appt_datetime = datetime(2017, 1, 11)
        self.assertTrue(weekday(base_appt_datetime.weekday()), WE)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime, subject_identifier="1234567890"
        )
        self.assertTrue(weekday(appt_datetimes[0].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), FR)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TU)

