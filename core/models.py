from django.db import models


class Page(models.Model):
    slug = models.SlugField()
    title = models.CharField("Page Title", max_length=50, blank=False,
                             help_text="Title text appears on the browsers tab.")
    heading = models.CharField("Page Heading", max_length=50, blank=False,
                               help_text="Heading text appears on the page.")
    content = models.TextField("Page Content", blank=True)


class HelpPage(Page):
    show = models.BooleanField("Show in menus")
    description = models.TextField("Search Description")
    activate = models.DateTimeField("Go live date/time", null=True, blank=True)
    deactivate = models.DateTimeField("Expiry date/time", null=True, blank=True)

    class Meta:
        verbose_name = "Help Page"
        verbose_name_plural = "Help Pages"