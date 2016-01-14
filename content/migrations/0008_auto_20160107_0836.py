# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_auto_20151211_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='levelquestion',
            name='image',
            field=models.ImageField(help_text=b"This is an icon and the ideal size for this icon is 32 x 32px. If the icon is bigger or smaller the phone's browser will scale it and the image will look very pixelated.", upload_to=b'questions/', null=True, verbose_name=b'Image', blank=True),
        ),
    ]
