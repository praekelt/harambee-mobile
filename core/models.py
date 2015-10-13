from django.db import models


class Page(models.Model):
    lookup = models.TextField()
    title = models.TextField("Page Title")
    heading = models.TextField("Page Heading")
    content = models.TextField("Page Content")