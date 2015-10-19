# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HarambeeLevelRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.PositiveIntegerField(default=0, choices=[(0, b'Active'), (1, b'Passed'), (2, b'Complete')])),
                ('date_completed', models.DateTimeField(null=True, verbose_name=b'Date Completed', blank=True)),
                ('harambee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HarambeeModuleRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('harambee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HarambeeQuestionAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_answered', models.DateTimeField()),
                ('harambee', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Level Question Answer',
                'verbose_name_plural': 'Level Question Answers',
            },
        ),
        migrations.CreateModel(
            name='Journey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('intro_text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('slug', models.SlugField(unique=True, verbose_name=b'Slug')),
                ('title', models.CharField(max_length=500, null=True, verbose_name=b'Title')),
                ('show_menu', models.BooleanField(default=True, verbose_name=b'Show in menus')),
                ('search', models.CharField(max_length=500, null=True, verbose_name=b'Search description')),
                ('image', models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True)),
                ('start_date', models.DateTimeField(null=True, verbose_name=b'Go Live On', blank=True)),
                ('end_date', models.DateTimeField(null=True, verbose_name=b'Expire On', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500, unique=True, null=True, verbose_name=b'Name')),
                ('text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('question_order', models.PositiveIntegerField(default=1, verbose_name=b'Question Order', choices=[(0, b'Ordered'), (1, b'Random')])),
                ('image', models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True)),
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
                ('image', models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True)),
                ('accessibleTo', models.PositiveIntegerField(default=1, verbose_name=b'Accessible To', choices=[(1, b'All'), (2, b'Learning Potential Score 1 - 4'), (3, b'Learning Potential Score 5+')])),
                ('show_recommended', models.BooleanField(default=True, verbose_name=b'Feature in Recommended for You')),
                ('slug', models.SlugField(unique=True, verbose_name=b'Slug')),
                ('title', models.CharField(max_length=500, null=True, verbose_name=b'Page Title')),
                ('show_menu', models.BooleanField(default=True, verbose_name=b'Show in menus')),
                ('search', models.CharField(max_length=500, null=True, verbose_name=b'Search description')),
                ('minimum_questions', models.PositiveIntegerField(verbose_name=b'Minimum questions answered')),
                ('minimum_percentage', models.PositiveIntegerField(verbose_name=b'Minimum % gained for all questions answered', choices=[(0, b'0%'), (25, b'25%'), (50, b'50%'), (75, b'75%'), (80, b'80%'), (90, b'90%'), (100, b'100%')])),
                ('store_data_per_user', models.BooleanField(default=True, verbose_name=b'Data stored against User I.D.')),
                ('start_date', models.DateTimeField(null=True, verbose_name=b'Go Live On', blank=True)),
                ('end_date', models.DateTimeField(null=True, verbose_name=b'Expire On', blank=True)),
                ('publish_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Published On')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name=b'Last Modified')),
                ('journeys', models.ManyToManyField(to='content.Journey')),
            ],
        ),
        migrations.AddField(
            model_name='level',
            name='module',
            field=models.ForeignKey(to='content.Module', null=True),
        ),
        migrations.AddField(
            model_name='harambeequestionanswer',
            name='option_selected',
            field=models.ForeignKey(to='content.LevelQuestionOption'),
        ),
        migrations.AddField(
            model_name='harambeequestionanswer',
            name='question',
            field=models.ForeignKey(to='content.LevelQuestion'),
        ),
        migrations.AddField(
            model_name='harambeemodulerel',
            name='module',
            field=models.ForeignKey(to='content.Module'),
        ),
        migrations.AddField(
            model_name='harambeelevelrel',
            name='level',
            field=models.ForeignKey(to='content.Level'),
        ),
    ]
