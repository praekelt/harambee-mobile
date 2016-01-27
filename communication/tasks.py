from celery import task
from communication.models import Sms, InactiveSMS
from rolefit.communication import send_sms, send_immediate_sms, send_bulk_sms
import httplib2
from django.utils import timezone
from datetime import datetime, timedelta
from my_auth.models import Harambee
from content.models import JourneyModuleRel, Module


@task
def send_smses():
    smses = Sms.objects.filter(sent=False)
    fail = 0

    for sms in smses:
        if fail < 3:
            try:
                send_sms(sms.harambee.candidate_id, sms.message)
            except (ValueError, httplib2.ServerNotFoundError):
                fail += 1

            sms.sent = True
            sms.time_sent = datetime.now()
            sms.save()


@task
def send_single_sms(harambee, message):
    try:
        send_sms(harambee.candidate_id, message)
        Sms.objects.create(harambee=harambee, message=message, sent=True, time_sent=datetime.now())
    except (ValueError, httplib2.ServerNotFoundError):
        Sms.objects.create(harambee=harambee, message=message)


@task
def send_immediate_sms(harambee, message):
    try:
        send_immediate_sms(harambee.candidate_id, message)
        Sms.objects.create(harambee=harambee, message=message, sent=True, time_sent=datetime.now())
    except (ValueError, httplib2.ServerNotFoundError):
        Sms.objects.create(harambee=harambee, message=message)


@task
def send_bulk_sms(harambee_list, message):
    try:
        candiate_id_list = harambee_list.values_list('candidate_id', flat=True)
        send_bulk_sms(candiate_id_list, message)
        for harambee in harambee_list:
            Sms.objects.create(harambee=harambee, message=message, sent=True, time_sent=datetime.now())
    except (ValueError, httplib2.ServerNotFoundError):
        for harambee in harambee_list:
            Sms.objects.create(harambee=harambee, message=message)


@task
def send_inactive_sms():
    """
        Loop through InactiveSMS objects and call sms_inactive_harambees method
    """
    queryset = InactiveSMS.objects.all().order_by('days')
    used_ids = []
    for item in queryset:
        used_ids = sms_inactive_harambees(used_ids, item.days, item.message)


def sms_inactive_harambees(used_ids, num_days, message):
    """
        Sends(Creates) an sms to each inactive harambee. Only harambees who's id is not in used_ids are smsed

        :param used_ids: List of harmabee ids already smsed
        :param num_days: Number of inactive days
        :param message: Text to be sent to in the SMS
        :return: list of used harambee ids smsed
        :rtype: list
    """
    date = timezone.now() - timedelta(days=num_days)
    queryset = Harambee.objects.filter(last_login__lt=date).exclude(id__in=used_ids)
    for harambee in queryset:
        harambee.send_sms(message)
    return used_ids + list(queryset.values_list('id', flat=True))


@task
def send_new_content_sms():
    """
        Nofify Harambees of newly published content.
    """
    today = datetime.now()
    new_modules = JourneyModuleRel.objects.filter(notified_users=False, module__start_date__lt=today)
    if new_modules:
        message = 'New modules have been published on Harambee:\n'

        lps_all = new_modules.filter(lps=Module.ALL)
        message_all = ''
        for item in lps_all:
            message_all += '* %s\n' % item.module.name
            item.module.notified_users = True
            item.save()

        lps_4 = new_modules.filter(lps=Module.LPS_1_4)
        message_4 = ''
        for item in lps_4:
            message_4 += '* %s\n' % item.module.name
            item.module.notified_users = True
            item.save()

        lps_5 = new_modules.filter(lps=Module.LPS_5)
        message_5 = ''
        for item in lps_5:
            message_5 += '* %s\n' % item.module.name
            item.module.notified_users = True
            item.save()

        #TODO: can replace with bulk. But then just add filter for receive_smses
        queryset = Harambee.objects.filter(lps__gte=5)
        for item in queryset:
            message = message + message_all + message_4 + message_5
            item.send_sms(message)

        queryset = Harambee.objects.filter(lps__lt=5)
        for item in queryset:
            message = message + message_all + message_4
            item.send_sms(message)
