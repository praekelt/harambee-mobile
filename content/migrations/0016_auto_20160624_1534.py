# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_auto_20160303_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='minimum_percentage',
            field=models.PositiveIntegerField(help_text=b'Required overall % to pass a level.', verbose_name=b'Minimum overall % for all questions answered', choices=[(0, b'0%'), (25, b'25%'), (50, b'50%'), (55, b'55%'), (60, b'60%'), (65, b'65%'), (70, b'70%'), (75, b'75%'), (80, b'80%'), (85, b'85%'), (90, b'90%'), (95, b'95%'), (100, b'100%')]),
        ),
    ]
