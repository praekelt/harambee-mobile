# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_auto_20160115_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='levelquestion',
            name='image',
            field=models.ImageField(help_text=b"This is an image and the ideal size for this image should be 150px in width. If the image width is bigger or smaller the phone's browser will scale it and the image will look very pixelated.", upload_to=b'questions/', null=True, verbose_name=b'Image', blank=True),
        ),
    ]
