from celery import task
from communication.models import Sms, InactiveSMS
from rolefit.communication import send_sms, send_immediate_sms, send_bulk_sms
import httplib2
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from my_auth.models import Harambee
from content.models import Module


@task
def send_smses():
    """
        Method loops through all the SMSes that have not been sent and attempts to send them again. If successful the
        SMS's sent field is set to True.
    """
    smses = Sms.objects.filter(sent=False)
    fail = 0

    for sms in smses:
        if fail < 3:
            try:
                send_sms(sms.harambee.candidate_id, sms.message)
            except (ValueError, httplib2.ServerNotFoundError):
                fail += 1

            sms.sent = True
            sms.time_sent = timezone.now()
            sms.save()


@task
def send_single_sms(harambee, message):
    """
        Method sends an SMS to a passed harambee. If the SMS is sent a SMS object is created with sent field set to True
        , else it is created with a sent field set to False.

        :param harambee: Harambee object
        :param message: String text
    """
    try:
        send_sms(harambee.candidate_id, message)
        Sms.objects.create(harambee=harambee, message=message, sent=True, time_sent=timezone.now())
    except (ValueError, httplib2.ServerNotFoundError):
        Sms.objects.create(harambee=harambee, message=message)


@task
def send_immediate_sms(harambee, message):
    """
        Method sends an SMS to a passed harambee. If the SMS is sent a SMS object is created with sent field set to True
        , else it is created with a sent field set to False. The method differs from send_single_sms method by calling
         send_immediate_sms which sends an sms immediately on Omnicor's side. There is no delay.

        :param harambee: Harambee object
        :param message: String
    """
    try:
        send_immediate_sms(harambee.candidate_id, message)
        Sms.objects.create(harambee=harambee, message=message, sent=True, time_sent=timezone.now())
    except (ValueError, httplib2.ServerNotFoundError):
        Sms.objects.create(harambee=harambee, message=message)


@task
def send_bulk_sms(harambee_list, message):
    """
        Method send an SMS to passed harambee list. If the call is successful an SMS object is created for each harambee
        with sent field set to True, else it is created with a sent field set to False.

        :param harambee_list: Harambee queryset
        :param message: String
    """
    try:
        candiate_id_list = harambee_list.values_list('candidate_id', flat=True)
        send_bulk_sms(candiate_id_list, message)
        for harambee in harambee_list:
            Sms.objects.create(harambee=harambee, message=message, sent=True, time_sent=timezone.now())
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
        Send an SMS to Harambees with a list of newly published Modules. Modules in the message are determined according
        to harmabees lps.
    """
    today = timezone.now()
    new_modules = Module.objects.filter(notified_users=False, start_date__lt=today)
    if new_modules:
        message_heading = 'New modules have been published on Harambee:\n'

        lps_all = new_modules.filter(accessibleTo=Module.ALL)
        message_all = ''
        for item in lps_all:
            message_all += '* %s\n' % item.name
            item.notified_users = True
            item.save()

        lps_4 = new_modules.filter(accessibleTo=Module.LPS_1_4)
        message_4 = ''
        for item in lps_4:
            message_4 += '* %s\n' % item.name
            item.notified_users = True
            item.save()

        lps_5 = new_modules.filter(accessibleTo=Module.LPS_5)
        message_5 = ''
        for item in lps_5:
            message_5 += '* %s\n' % item.name
            item.notified_users = True
            item.save()

        #TODO: can replace with bulk. But then just add filter for receive_smses
        queryset = Harambee.objects.filter(lps__gte=5)
        for item in queryset:
            message = message_heading + message_all + message_4 + message_5
            item.send_sms(message)

        queryset = Harambee.objects.filter(lps__lt=5)
        for item in queryset:
            message = message_heading + message_all + message_4
            item.send_sms(message)
