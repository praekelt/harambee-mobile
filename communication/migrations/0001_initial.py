# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_auth', '0002_harambee_candidate_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sent', models.BooleanField(default=False, verbose_name=b'Sent')),
                ('message', models.TextField(verbose_name=b'Message')),
                ('time_sent', models.DateTimeField(verbose_name=b'Time sent', blank=True)),
                ('harambee', models.ForeignKey(related_name='User', to='my_auth.Harambee', null=True)),
            ],
        ),
    ]
