# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def add_pages(apps, schema_editor):
        page = apps.get_model("core", "Page")

        page.objects.create(slug="successful_mobile_change",
                            title="Mobile Number Change",
                            heading="Mobile Number Change Successful")

        page.objects.create(slug="successful_pin_change",
                            title="PIN Change",
                            heading="PIN Change Successful")

    dependencies = [
        ('core', '0002_auto_20151015_1318'),
    ]

    operations = [
        migrations.RunPython(add_pages)
    ]
