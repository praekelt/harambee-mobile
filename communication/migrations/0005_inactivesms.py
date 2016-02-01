# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0004_sms_date_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='InactiveSMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('days', models.PositiveIntegerField(verbose_name=b'Days inactive')),
                ('message', models.TextField(verbose_name=b'Message')),
            ],
            options={
                'verbose_name': 'Inactive SMS',
                'verbose_name_plural': 'Inactive SMSes',
            },
        ),
    ]
