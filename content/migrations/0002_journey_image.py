# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='journey',
            name='image',
            field=models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True),
        ),
    ]
