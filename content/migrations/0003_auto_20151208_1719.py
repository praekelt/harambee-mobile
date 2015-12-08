# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_auto_20151113_2205'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='harambeejourneymodulerel',
            options={'verbose_name': 'Harambee Module Relationship', 'verbose_name_plural': 'Harambee Module Relationships'},
        ),
    ]
