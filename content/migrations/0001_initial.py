# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Journey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('intro_text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('slug', models.TextField(verbose_name=b'Slug', blank=True)),
                ('show_menu', models.BooleanField(default=True, verbose_name=b'Show in menus')),
                ('search', models.CharField(max_length=500, null=True, verbose_name=b'Search description')),
                ('start_date', models.DateTimeField(verbose_name=b'Go Live On')),
                ('end_date', models.DateTimeField(verbose_name=b'Expire On')),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LevelQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('description', models.CharField(max_length=500, verbose_name=b'Description', blank=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name=b'Order')),
                ('question_content', models.TextField(verbose_name=b'Question', blank=True)),
                ('answer_content', models.TextField(verbose_name=b'Fully Worked Solution', blank=True)),
                ('notes', models.TextField(verbose_name=b'Additional Notes', blank=True)),
                ('image', models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True)),
                ('level', models.ForeignKey(to='content.Level', null=True)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Level Question',
                'verbose_name_plural': 'Level Questions',
            },
        ),
        migrations.CreateModel(
            name='LevelQuestionOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('order', models.PositiveIntegerField(default=0, verbose_name=b'Order')),
                ('content', models.TextField(verbose_name=b'Content', blank=True)),
                ('correct', models.BooleanField(verbose_name=b'Correct')),
                ('question', models.ForeignKey(to='content.LevelQuestion', null=True)),
            ],
            options={
                'verbose_name': 'Question Option',
                'verbose_name_plural': 'Question Options',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('intro_text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('end_text', models.TextField(verbose_name=b'Complete Page Text', blank=True)),
                ('accessibleTo', models.PositiveIntegerField(default=1, verbose_name=b'Accessible To', choices=[(1, b'All'), (2, b'Learning Potential Score 1 - 4'), (3, b'Learning Potential Score 5+')])),
                ('show_recomended', models.BooleanField(default=True, verbose_name=b'Feature in Recomended for You')),
                ('slug', models.TextField(verbose_name=b'Slug', blank=True)),
                ('title', models.CharField(max_length=500, null=True, verbose_name=b'Page Title')),
                ('show_menu', models.BooleanField(default=True, verbose_name=b'Show in menus')),
                ('search', models.CharField(max_length=500, null=True, verbose_name=b'Search description')),
                ('minimum_questions', models.PositiveIntegerField(verbose_name=b'Minimum questions answered')),
                ('minimum_percentage', models.PositiveIntegerField(verbose_name=b'Minimum % gained for all questions answered', choices=[(0, b'0%'), (1, b'25%'), (2, b'50%'), (3, b'75%'), (4, b'80%'), (5, b'90%'), (6, b'100%')])),
                ('store_data_per_user', models.BooleanField(default=True, verbose_name=b'Data stored against User I.D.')),
                ('start_date', models.DateTimeField(verbose_name=b'Go Live On')),
                ('end_date', models.DateTimeField(verbose_name=b'Expire On')),
                ('publish_date', models.DateTimeField(verbose_name=b'Published On')),
                ('journeys', models.ManyToManyField(to='content.Journey')),
            ],
        ),
        migrations.AddField(
            model_name='level',
            name='module',
            field=models.ForeignKey(to='content.Module', null=True),
        ),
    ]
