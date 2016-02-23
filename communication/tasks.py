from celery import task
from communication.models import Sms, InactiveSMS
from rolefit.communication import send_sms, send_immediate_sms, send_bulk_sms
import httplib2
from datetime import timedelta
from django.utils import timezone
from my_auth.models import Harambee
from content.models import Module
from django.db.models import F


@task
def send_smses():
    """
        Method loops through all the SMSes that have not been sent and attempts to send them again. If successful the
        SMS's sent field is set to True.
    """
    smses = Sms.objects.filter(sent=False)
    fail = 0

    for sms in smses:
        sent = False
        if fail < 3:
            try:
                send_sms(sms.harambee.candidate_id, sms.message)
                sent = True
            except (ValueError, httplib2.ServerNotFoundError):
                fail += 1

        if sent:
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
def send_immediate_sms_task(harambee, message):
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
        Loop through InactiveSMS objects and call sms_inactive_harambees method. Send SMS only to users who have only
        logged in once.
    """
    inactive_harambees = Harambee.objects.extra(where=['last_login::date = date_joined::date'])
    if inactive_harambees:
        #values_list() crashes and burns the poor Django, therefore used a loop to extract the ids
        inactive_ids = list()
        for h in inactive_harambees:
            inactive_ids.append(h.id)
        used_ids = list(Harambee.objects.exclude(id__in=inactive_ids).values_list('id', flat=True))
        queryset = InactiveSMS.objects.all().order_by('days')
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
    queryset = Harambee.objects\
        .filter(last_login__year=date.year, last_login__month=date.month, last_login__day=date.day,)\
        .exclude(id__in=used_ids)
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
        message = '#HarambeeLearning. Exciting news! New modules are available on Harambee4work.mobi. ' \
                  'Log on now and continue your learning journey with us!'

        lps_all = new_modules.filter(accessibleTo=Module.ALL)
        m_all = m_4 = m_5 = False
        for item in lps_all:
            m_all = True
            item.notified_users = True
            item.save()

        lps_4 = new_modules.filter(accessibleTo=Module.LPS_1_4)
        for item in lps_4:
            m_4 = True
            item.notified_users = True
            item.save()

        lps_5 = new_modules.filter(accessibleTo=Module.LPS_5)
        for item in lps_5:
            m_5 = True
            item.notified_users = True
            item.save()

        #TODO: can replace with bulk. But then just add filter for receive_smses
        if m_all or m_5:
            queryset = Harambee.objects.filter(lps__gte=5)
            for item in queryset:
                item.send_sms(message)

        if m_all or m_4:
            queryset = Harambee.objects.filter(lps__lt=5)
            for item in queryset:
                item.send_sms(message)
