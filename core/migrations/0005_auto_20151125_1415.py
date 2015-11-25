# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_page_content(apps, schema_editor):
    page = apps.get_model("core", "Page")

    db_page = page.objects.filter(slug="completed_modules")

    if db_page:
        db_page.update(content="Here you can find all your completed modules. If you do not feel that you "
                               "have mastered a module you can choose to redo it anytime from the list below")
    else:
        print "Can't find page"


def revert_page_content(apps, schema_editor):
    page = apps.get_model("core", "Page")

    db_page = page.objects.filter(slug="completed_modules")

    if db_page:
        db_page.update(content="Here you can find all your completed modules. If you feel you have not mastered a"
                               " module you choose to redo it any time from the list below")
    else:
        print "Can't find page"


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20151125_0456'),
    ]

    operations = [
        migrations.RunPython(update_page_content, revert_page_content)
    ]
