# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HarambeeJourneyModuleLevelRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.PositiveIntegerField(default=0, choices=[(0, b'Active'), (1, b'Complete')])),
                ('level_passed', models.BooleanField(default=False)),
                ('date_started', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Started', null=True)),
                ('date_completed', models.DateTimeField(null=True, verbose_name=b'Date Completed', blank=True)),
                ('level_attempt', models.PositiveIntegerField(verbose_name=b'Attempt Number')),
            ],
        ),
        migrations.CreateModel(
            name='HarambeeJourneyModuleRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.PositiveIntegerField(default=0, choices=[(0, b'Active'), (1, b'Complete')])),
                ('date_started', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Started', null=True)),
                ('date_completed', models.DateTimeField(null=True, verbose_name=b'Date Completed', blank=True)),
                ('harambee', models.ForeignKey(to='my_auth.Harambee')),
            ],
        ),
        migrations.CreateModel(
            name='HarambeeQuestionAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_answered', models.DateTimeField()),
                ('harambee', models.ForeignKey(to='my_auth.Harambee')),
                ('harambee_level_rel', models.ForeignKey(to='content.HarambeeJourneyModuleLevelRel')),
            ],
            options={
                'verbose_name': 'Level Question Answer',
                'verbose_name_plural': 'Level Question Answers',
            },
        ),
        migrations.CreateModel(
            name='HarambeeState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active_level_rel', models.ForeignKey(blank=True, to='content.HarambeeJourneyModuleLevelRel', null=True)),
                ('harambee', models.ForeignKey(to='my_auth.Harambee')),
            ],
        ),
        migrations.CreateModel(
            name='Journey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=500, verbose_name=b'Name')),
                ('intro_text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('slug', models.SlugField(help_text=b'Slug used to identify this journey in URL. Must be unique.e.g. Journey_101', unique=True, verbose_name=b'Slug')),
                ('title', models.CharField(help_text=b'Title is displayed in the browsers tab.', max_length=500, verbose_name=b'Title')),
                ('show_menu', models.BooleanField(default=True, help_text=b'Show the journey link in users menu?', verbose_name=b'Show in menus')),
                ('search', models.CharField(max_length=500, verbose_name=b'Search description')),
                ('image', models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True)),
                ('colour', models.CharField(help_text=b'Colour theme for the journey. Hexadecimal colour value. e.g. #A6CE39', max_length=7, verbose_name=b'Colour')),
                ('start_date', models.DateTimeField(null=True, verbose_name=b'Go Live On', blank=True)),
                ('end_date', models.DateTimeField(null=True, verbose_name=b'Expire On', blank=True)),
                ('publish_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Published On')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name=b'Last Modified')),
            ],
        ),
        migrations.CreateModel(
            name='JourneyModuleRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('journey', models.ForeignKey(to='content.Journey')),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=500, verbose_name=b'Name')),
                ('text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('order', models.PositiveIntegerField(help_text=b'Levels are completed according to this number.', verbose_name=b'Level number')),
                ('question_order', models.PositiveIntegerField(default=1, help_text=b'Order in which questions will be chosen.', verbose_name=b'Question Order', choices=[(0, b'Ordered'), (1, b'Random')])),
            ],
        ),
        migrations.CreateModel(
            name='LevelQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=500, verbose_name=b'Name')),
                ('description', models.CharField(max_length=500, verbose_name=b'Description', blank=True)),
                ('order', models.PositiveIntegerField(help_text=b'Order number determines the order in which questions are asked in a level.', verbose_name=b'Order Number')),
                ('question_content', models.TextField(verbose_name=b'Question')),
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
                ('content', models.TextField(verbose_name=b'Content')),
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
                ('name', models.CharField(unique=True, max_length=500, verbose_name=b'Name')),
                ('intro_text', models.TextField(verbose_name=b'Introductory Text', blank=True)),
                ('end_text', models.TextField(verbose_name=b'Complete Page Text', blank=True)),
                ('image', models.ImageField(upload_to=b'img/', null=True, verbose_name=b'Image', blank=True)),
                ('accessibleTo', models.PositiveIntegerField(default=1, verbose_name=b'Accessible To', choices=[(1, b'All'), (2, b'Learning Potential Score 1 - 4'), (3, b'Learning Potential Score 5+')])),
                ('show_recommended', models.BooleanField(default=True, verbose_name=b'Feature in Recommended for You')),
                ('slug', models.SlugField(help_text=b'Slug used to identify this module in URL. Must be unique.e.g. Module_101', unique=True, verbose_name=b'Slug')),
                ('title', models.CharField(help_text=b'Title is displayed in the browsers tab.', max_length=500, verbose_name=b'Page Title')),
                ('show_menu', models.BooleanField(default=True, help_text=b'Show the module link in users menu?', verbose_name=b'Show in menu')),
                ('search', models.CharField(max_length=500, verbose_name=b'Search description')),
                ('minimum_questions', models.PositiveIntegerField(help_text=b'Required number of questions to be answered to pass a level.', verbose_name=b'Minimum # of questions to answer')),
                ('minimum_percentage', models.PositiveIntegerField(help_text=b'Required overall % to pass a level.', verbose_name=b'Minimum overall % for all questions answered', choices=[(0, b'0%'), (25, b'25%'), (50, b'50%'), (75, b'75%'), (80, b'80%'), (90, b'90%'), (100, b'100%')])),
                ('store_data_per_user', models.BooleanField(default=True, verbose_name=b'Data stored against User I.D.')),
                ('start_date', models.DateTimeField(null=True, verbose_name=b'Go Live On', blank=True)),
                ('end_date', models.DateTimeField(null=True, verbose_name=b'Expire On', blank=True)),
                ('publish_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Published On')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name=b'Last Modified')),
                ('journeys', models.ManyToManyField(related_name='modules', through='content.JourneyModuleRel', to='content.Journey')),
            ],
        ),
        migrations.AddField(
            model_name='level',
            name='module',
            field=models.ForeignKey(to='content.Module', null=True),
        ),
        migrations.AddField(
            model_name='journeymodulerel',
            name='module',
            field=models.ForeignKey(to='content.Module'),
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
            model_name='harambeejourneymodulerel',
            name='journey_module_rel',
            field=models.ForeignKey(to='content.JourneyModuleRel'),
        ),
        migrations.AddField(
            model_name='harambeejourneymodulelevelrel',
            name='current_question',
            field=models.ForeignKey(blank=True, to='content.LevelQuestion', null=True),
        ),
        migrations.AddField(
            model_name='harambeejourneymodulelevelrel',
            name='harambee_journey_module_rel',
            field=models.ForeignKey(to='content.HarambeeJourneyModuleRel', null=True),
        ),
        migrations.AddField(
            model_name='harambeejourneymodulelevelrel',
            name='level',
            field=models.ForeignKey(to='content.Level'),
        ),
    ]
