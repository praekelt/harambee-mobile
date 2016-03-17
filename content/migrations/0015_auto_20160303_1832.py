# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_auto_20160128_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harambeejourneymodulerel',
            name='state',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'Active'), (1, b'Half Way'), (2, b'Completed')]),
        ),
    ]
