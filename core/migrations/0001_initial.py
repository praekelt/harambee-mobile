# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('title', models.CharField(help_text=b'Title text appears on the browsers tab.', max_length=50, verbose_name=b'Page Title')),
                ('heading', models.CharField(help_text=b'Heading text appears on the page.', max_length=50, verbose_name=b'Page Heading')),
                ('content', models.TextField(verbose_name=b'Page Content', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HelpPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.Page')),
                ('show', models.BooleanField(verbose_name=b'Show in menus')),
                ('description', models.TextField(verbose_name=b'Search Description')),
                ('activate', models.DateTimeField(null=True, verbose_name=b'Go live date/time', blank=True)),
                ('deactivate', models.DateTimeField(null=True, verbose_name=b'Expiry date/time', blank=True)),
            ],
            options={
                'verbose_name': 'Help Page',
                'verbose_name_plural': 'Help Pages',
            },
            bases=('core.page',),
        ),
    ]
