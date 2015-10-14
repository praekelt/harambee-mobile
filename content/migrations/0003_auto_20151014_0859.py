# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_journey_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='show_recomended',
        ),
        migrations.AddField(
            model_name='module',
            name='show_recommended',
            field=models.BooleanField(default=True, verbose_name=b'Feature in Recommended for You'),
        ),
        migrations.AlterField(
            model_name='journey',
            name='slug',
            field=models.SlugField(verbose_name=b'Slug'),
        ),
        migrations.AlterField(
            model_name='module',
            name='slug',
            field=models.SlugField(verbose_name=b'Slug'),
        ),
    ]
