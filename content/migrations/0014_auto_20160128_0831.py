# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_module_state(apps, schema_editor):
    """
        MODULE_COMPLETE constant (now called MODULE_COMPLETED) had a value of 1, which is now taken by MODULE_HALF
        constant. MODULE_COMPLETED's new value is 2. This data migration updates the existing objects.
    """
    HarambeeJourneyModuleRel = apps.get_model('content', 'HarambeeJourneyModuleRel')
    HarambeeJourneyModuleRel.objects.filter(state=1)\
        .update(state=HarambeeJourneyModuleRel.MODULE_COMPLETED)


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_module_notified_users'),
    ]

    operations = [
        migrations.RunPython(update_module_state)
    ]
