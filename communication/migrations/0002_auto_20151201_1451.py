# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sms',
            options={'verbose_name': 'SMS', 'verbose_name_plural': 'SMSes'},
        ),
    ]
