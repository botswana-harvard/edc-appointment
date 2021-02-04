# Generated by Django 2.1.7 on 2019-03-04 23:23

import django_audit_fields.fields.hostname_modification_field
import django_audit_fields.fields.userfield
import django_audit_fields.models.audit_model_mixin
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("edc_appointment", "0017_auto_20190201_0446")]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="created",
            field=models.DateTimeField(
                blank=True, default=django_audit_fields.models.audit_model_mixin.utcnow
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="hostname_modified",
            field=django_audit_fields.fields.hostname_modification_field.HostnameModificationField(
                blank=True,
                help_text="System field. (modified on every save)",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="modified",
            field=models.DateTimeField(
                blank=True, default=django_audit_fields.models.audit_model_mixin.utcnow
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="user_created",
            field=django_audit_fields.fields.userfield.UserField(
                blank=True,
                help_text="Updated by admin.save_model",
                max_length=50,
                verbose_name="user created",
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="user_modified",
            field=django_audit_fields.fields.userfield.UserField(
                blank=True,
                help_text="Updated by admin.save_model",
                max_length=50,
                verbose_name="user modified",
            ),
        ),
        migrations.AlterField(
            model_name="historicalappointment",
            name="created",
            field=models.DateTimeField(
                blank=True, default=django_audit_fields.models.audit_model_mixin.utcnow
            ),
        ),
        migrations.AlterField(
            model_name="historicalappointment",
            name="hostname_modified",
            field=django_audit_fields.fields.hostname_modification_field.HostnameModificationField(
                blank=True,
                help_text="System field. (modified on every save)",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="historicalappointment",
            name="modified",
            field=models.DateTimeField(
                blank=True, default=django_audit_fields.models.audit_model_mixin.utcnow
            ),
        ),
        migrations.AlterField(
            model_name="historicalappointment",
            name="user_created",
            field=django_audit_fields.fields.userfield.UserField(
                blank=True,
                help_text="Updated by admin.save_model",
                max_length=50,
                verbose_name="user created",
            ),
        ),
        migrations.AlterField(
            model_name="historicalappointment",
            name="user_modified",
            field=django_audit_fields.fields.userfield.UserField(
                blank=True,
                help_text="Updated by admin.save_model",
                max_length=50,
                verbose_name="user modified",
            ),
        ),
    ]
