# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0002_auto_20151201_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms',
            name='time_sent',
            field=models.DateTimeField(null=True, verbose_name=b'Time sent', blank=True),
        ),
    ]
