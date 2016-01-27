# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def add_inactive_smses(apps, schema_editor):
        inactive_sms = apps.get_model("communication.InactiveSMS")

        inactive_sms.objects.create(days=2,
                                    message="You have been inactive for 2 days.")

        inactive_sms.objects.create(days=5,
                                    message="You have been inactive for 5 days.")

        inactive_sms.objects.create(days=12,
                                    message="You have been inactive for 12 days.")

        inactive_sms.objects.create(days=19,
                                    message="You have been inactive for 19 days.")

        inactive_sms.objects.create(days=30,
                                    message="You have been inactive for 30 days.")

        inactive_sms.objects.create(days=90,
                                    message="You have been inactive for 90 days.")

        inactive_sms.objects.create(days=180,
                                    message="You have been inactive for 180 days.")

        inactive_sms.objects.create(days=360,
                                    message="You have been inactive for 360 days.")

    dependencies = [
        ('communication', '0005_inactivesms'),
    ]

    operations = [
        migrations.RunPython(add_inactive_smses)
    ]
