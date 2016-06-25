# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-25 09:42
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import django_revision.revision_field
import edc_base.model.fields.hostname_modification_field
import edc_base.model.fields.userfield
import edc_sync.models.sync_model_mixin
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('edc_visit_schedule', '__first__'),
        ('edc_appointment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentTestModel',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('user_created', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user created')),
                ('user_modified', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(default='ckgathi', editable=False, help_text='System field. (modified on create only)', max_length=50)),
                ('hostname_modified', edc_base.model.fields.hostname_modification_field.HostnameModificationField(editable=False, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('id', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('appointment_identifier', models.CharField(blank=True, db_index=True, max_length=50, unique=True, verbose_name='Identifier')),
                ('best_appt_datetime', models.DateTimeField(editable=False, null=True)),
                ('appt_close_datetime', models.DateTimeField(editable=False, null=True)),
                ('visit_instance', models.CharField(blank=True, db_index=True, default='0', help_text='A decimal to represent an additional report to be included with the original visit report. (NNNN.0)', max_length=1, null=True, validators=[django.core.validators.RegexValidator('[0-9]', 'Must be a number from 0-9')], verbose_name='Instance')),
                ('appt_datetime', models.DateTimeField(db_index=True, verbose_name='Appointment date and time')),
                ('timepoint_datetime', models.DateTimeField(editable=False, help_text='calculated appointment datetime. Do not change', null=True, verbose_name='Timepoint date and time')),
                ('appt_status', models.CharField(choices=[('new', 'New'), ('in_progress', 'In Progress'), ('incomplete', 'Incomplete'), ('done', 'Done'), ('cancelled', 'Cancelled')], db_index=True, default='new', max_length=25, verbose_name='Status')),
                ('appt_reason', models.CharField(blank=True, help_text='Reason for appointment', max_length=25, verbose_name='Reason for appointment')),
                ('contact_tel', models.CharField(blank=True, max_length=250, verbose_name='Contact Tel')),
                ('comment', models.CharField(blank=True, max_length=250, verbose_name='Comment')),
                ('is_confirmed', models.BooleanField(default=False, editable=False)),
                ('contact_count', models.IntegerField(default=0, editable=False)),
                ('dashboard_type', models.CharField(blank=True, db_index=True, editable=False, help_text='hold dashboard_type variable, set by dashboard', max_length=25, null=True)),
                ('appt_type', models.CharField(choices=[('clinic', 'In clinic'), ('telephone', 'By telephone'), ('home', 'At home')], default='clinic', help_text='Default for subject may be edited in admin under section bhp_subject. See Subject Configuration.', max_length=20, verbose_name='Appointment type')),
            ],
        ),
        migrations.CreateModel(
            name='Crypt',
            fields=[
                ('hash', models.CharField(db_index=True, max_length=128, unique=True, verbose_name='Hash')),
                ('secret', models.BinaryField(verbose_name='Secret')),
                ('algorithm', models.CharField(db_index=True, max_length=25, null=True)),
                ('mode', models.CharField(db_index=True, max_length=25, null=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('user_created', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user created')),
                ('user_modified', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(default='ckgathi', editable=False, help_text='System field. (modified on create only)', max_length=50)),
                ('hostname_modified', edc_base.model.fields.hostname_modification_field.HostnameModificationField(editable=False, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('id', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
            ],
            bases=(edc_sync.models.sync_model_mixin.SyncMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalAppointmentTestModel',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('user_created', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user created')),
                ('user_modified', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(default='ckgathi', editable=False, help_text='System field. (modified on create only)', max_length=50)),
                ('hostname_modified', edc_base.model.fields.hostname_modification_field.HostnameModificationField(editable=False, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('id', models.UUIDField(blank=True, db_index=True, default=uuid.uuid4, editable=False, help_text='System auto field. UUID primary key.')),
                ('appointment_identifier', models.CharField(blank=True, db_index=True, max_length=50, verbose_name='Identifier')),
                ('best_appt_datetime', models.DateTimeField(editable=False, null=True)),
                ('appt_close_datetime', models.DateTimeField(editable=False, null=True)),
                ('visit_instance', models.CharField(blank=True, db_index=True, default='0', help_text='A decimal to represent an additional report to be included with the original visit report. (NNNN.0)', max_length=1, null=True, validators=[django.core.validators.RegexValidator('[0-9]', 'Must be a number from 0-9')], verbose_name='Instance')),
                ('appt_datetime', models.DateTimeField(db_index=True, verbose_name='Appointment date and time')),
                ('timepoint_datetime', models.DateTimeField(editable=False, help_text='calculated appointment datetime. Do not change', null=True, verbose_name='Timepoint date and time')),
                ('appt_status', models.CharField(choices=[('new', 'New'), ('in_progress', 'In Progress'), ('incomplete', 'Incomplete'), ('done', 'Done'), ('cancelled', 'Cancelled')], db_index=True, default='new', max_length=25, verbose_name='Status')),
                ('appt_reason', models.CharField(blank=True, help_text='Reason for appointment', max_length=25, verbose_name='Reason for appointment')),
                ('contact_tel', models.CharField(blank=True, max_length=250, verbose_name='Contact Tel')),
                ('comment', models.CharField(blank=True, max_length=250, verbose_name='Comment')),
                ('is_confirmed', models.BooleanField(default=False, editable=False)),
                ('contact_count', models.IntegerField(default=0, editable=False)),
                ('dashboard_type', models.CharField(blank=True, db_index=True, editable=False, help_text='hold dashboard_type variable, set by dashboard', max_length=25, null=True)),
                ('appt_type', models.CharField(choices=[('clinic', 'In clinic'), ('telephone', 'By telephone'), ('home', 'At home')], default='clinic', help_text='Default for subject may be edited in admin under section bhp_subject. See Subject Configuration.', max_length=20, verbose_name='Appointment type')),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical appointment test model',
            },
        ),
        migrations.CreateModel(
            name='RegisteredSubject',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('user_created', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user created')),
                ('user_modified', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(default='ckgathi', editable=False, help_text='System field. (modified on create only)', max_length=50)),
                ('hostname_modified', edc_base.model.fields.hostname_modification_field.HostnameModificationField(editable=False, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('id', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
                ('subject_identifier', models.CharField(blank=True, db_index=True, max_length=50, unique=True, verbose_name='Subject Identifier')),
                ('study_site', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('user_created', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user created')),
                ('user_modified', edc_base.model.fields.userfield.UserField(editable=False, max_length=50, verbose_name='user modified')),
                ('hostname_created', models.CharField(default='ckgathi', editable=False, help_text='System field. (modified on create only)', max_length=50)),
                ('hostname_modified', edc_base.model.fields.hostname_modification_field.HostnameModificationField(editable=False, help_text='System field. (modified on every save)', max_length=50)),
                ('revision', django_revision.revision_field.RevisionField(blank=True, editable=False, help_text='System field. Git repository tag:branch:commit.', max_length=75, null=True, verbose_name='Revision')),
                ('id', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, help_text='System auto field. UUID primary key.', primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='historicalappointmenttestmodel',
            name='registered_subject',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='example.RegisteredSubject'),
        ),
        migrations.AddField(
            model_name='historicalappointmenttestmodel',
            name='time_point_status',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='edc_appointment.TimePointStatus'),
        ),
        migrations.AddField(
            model_name='historicalappointmenttestmodel',
            name='visit_definition',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='edc_visit_schedule.VisitDefinition'),
        ),
        migrations.AlterUniqueTogether(
            name='crypt',
            unique_together=set([('hash', 'algorithm', 'mode')]),
        ),
        migrations.AddField(
            model_name='appointmenttestmodel',
            name='registered_subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='example.RegisteredSubject'),
        ),
        migrations.AddField(
            model_name='appointmenttestmodel',
            name='time_point_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='edc_appointment.TimePointStatus'),
        ),
        migrations.AddField(
            model_name='appointmenttestmodel',
            name='visit_definition',
            field=models.ForeignKey(help_text='For tracking within the window period of a visit, use the decimal convention. Format is NNNN.N. e.g 1000.0, 1000.1, 1000.2, etc)', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='edc_visit_schedule.VisitDefinition', verbose_name='Visit'),
        ),
    ]
