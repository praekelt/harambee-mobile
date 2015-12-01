from django.db import models
from my_auth.models import Harambee


class Sms(models.Model):
    sent = models.BooleanField('Sent', default=False)
    harambee = models.ForeignKey(Harambee, related_name='User', null=True, blank=False)
    message = models.TextField('Message', blank=False)
    time_sent = models.DateTimeField('Time sent', blank=True)

    class Meta:
        verbose_name = 'SMS'
        verbose_name_plural = 'SMSes'