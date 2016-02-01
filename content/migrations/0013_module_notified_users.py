# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160119_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='notified_users',
            field=models.BooleanField(default=False),
        ),
    ]
