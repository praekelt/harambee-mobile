# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_helppage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='lookup',
        ),
        migrations.AddField(
            model_name='page',
            name='slug',
            field=models.SlugField(default='welcome'),
            preserve_default=False,
        ),
    ]
