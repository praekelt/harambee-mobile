# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_auth', '0002_harambee_candidate_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='HarambeeLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('action', models.PositiveIntegerField(verbose_name=b'Action', choices=[(0, b'Login'), (1, b'Logout')])),
                ('harambee', models.ForeignKey(to='my_auth.Harambee', null=True)),
            ],
        ),
    ]
