# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_auth', '0003_harambeelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='harambee',
            name='receive_smses',
            field=models.BooleanField(default=True, verbose_name=b'Receive SMSes'),
        ),
    ]
