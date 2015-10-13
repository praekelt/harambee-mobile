from django.db import models
from django.contrib.auth.models import User


class Harambee(User):
    mobile = models.CharField(verbose_name="Mobile Phone Number", max_length=50, blank=False, unique=True)
    lps = models.PositiveIntegerField("Learning Potential Score")

    REQUIRED_FIELDS = ["mobile"]

    class Meta:
        verbose_name = "Harambee"
        verbose_name_plural = "Harambees"


class SystemAdministrator(User):

    class Meta:
        verbose_name = "System Administrator"
        verbose_name_plural = "System Administrators"

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_superuser = True
        super(SystemAdministrator, self).save(*args, **kwargs)
