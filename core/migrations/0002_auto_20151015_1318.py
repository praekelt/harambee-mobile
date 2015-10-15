# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def add_pages(apps, schema_editor):

        page = apps.get_model("core", "Page")

        page.objects.create(slug="welcome",
                            title="WELCOME",
                            heading="Welcome",
                            content="Are you 18 - 28 years old, with a matric, diploma/degree and struggling to find "
                                    "a job? Harambee can help you! \r\n\r\nGo on a journey of career discovery and "
                                    "learn what it takes to get the job is right for you!")

        page.objects.create(slug="join",
                            title="JOIN",
                            heading="Join")

        page.objects.create(slug="why_id",
                            title="WHY DO WE NEED YOUR I.D. NUMBER?",
                            heading="Why do we need your I.D. number?",
                            content="")

        page.objects.create(slug="login",
                            title="LOG IN",
                            heading="Log In")

        page.objects.create(slug="forgot_pin",
                            title="FORGOTTEN PIN",
                            heading="No Problem",
                            content="Just give us your I.D. number and we'll send an SMS to the number we have on file "
                                    "for you with your new PIN.")

        page.objects.create(slug="send_pin",
                            title="SEND PIN",
                            heading="Done.",
                            content="Your new PIN will be sent to you by SMS shortly. Use the new PIN with your usual "
                                    "I.D. number to login.")

        page.objects.create(slug="no_match",
                            title="NO MATCH",
                            heading="No match.",
                            content="Sorry your I.D. number does not match any Harambees we have on record. Right now, "
                                    "only those that have attended training at Harambee can join this platform.")

        page.objects.create(slug="intro",
                            title="INTRODUCTION",
                            heading="Introduction",
                            content="Get started by choosing which journey you'd like to explore...")

        page.objects.create(slug="home",
                            title="HOME",
                            heading="Home")

        page.objects.create(slug="about",
                            title="ABOUT",
                            heading="About Harambee",
                            content="")

        page.objects.create(slug="contact",
                            title="CONTACT US",
                            heading="Contact Us",
                            content="")

        page.objects.create(slug="terms",
                            title="TERMS AND CONDITIONS",
                            heading="Terms and Conditions",
                            content="")


    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_pages)
    ]
