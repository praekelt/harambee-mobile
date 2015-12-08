# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20151208_1719'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='harambeejourneymodulelevelrel',
            options={'verbose_name': 'Harambee Level Relationship', 'verbose_name_plural': 'Harambee Level Relationships'},
        ),
    ]
