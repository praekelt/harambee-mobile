# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journey',
            name='image',
            field=models.ImageField(upload_to=b'journeys/', null=True, verbose_name=b'Image', blank=True),
        ),
        migrations.AlterField(
            model_name='levelquestion',
            name='image',
            field=models.ImageField(upload_to=b'questions/', null=True, verbose_name=b'Image', blank=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='image',
            field=models.ImageField(upload_to=b'modules/', null=True, verbose_name=b'Image', blank=True),
        ),
    ]
