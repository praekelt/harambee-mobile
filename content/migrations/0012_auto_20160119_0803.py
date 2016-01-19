# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_auto_20160115_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='levelquestion',
            name='name',
            field=models.CharField(default=b'Auto Generated', unique=True, max_length=500, verbose_name=b'Name'),
        ),
    ]
