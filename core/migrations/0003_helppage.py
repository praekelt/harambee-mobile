# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_page_heading'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Page')),
            ],
            options={
                'verbose_name': 'Help Page',
                'verbose_name_plural': 'Help Pages',
            },
            bases=('core.page',),
        ),
    ]
