from django.db import models


class Sms(models.Model):
    sent = models.BooleanField('Sent', default=False)
    harambee = models.ForeignKey('my_auth.Harambee', related_name='User', null=True, blank=False)
    message = models.TextField('Message', blank=False)
    time_sent = models.DateTimeField('Time sent', null=True, blank=True)
    date_created = models.DateTimeField('Date created', auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = 'SMS'
        verbose_name_plural = 'SMSes'


class InactiveSMS(models.Model):
    days = models.PositiveIntegerField('Days inactive')
    message = models.TextField('Message')

    class Meta:
        verbose_name = 'Inactive SMS'
        verbose_name_plural = 'Inactive SMSes'
