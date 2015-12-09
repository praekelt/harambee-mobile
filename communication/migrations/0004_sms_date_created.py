# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0003_auto_20151201_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Date created', null=True),
        ),
    ]
