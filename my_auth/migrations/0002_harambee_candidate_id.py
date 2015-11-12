# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='harambee',
            name='candidate_id',
            field=models.CharField(default=0, unique=True, max_length=20, verbose_name=b'Rolefit Candidate Id'),
            preserve_default=False,
        ),
    ]
