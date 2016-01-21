from celery import task
from communication.models import Sms
from rolefit.communication import send_sms, send_immediate_sms
import httplib2
from datetime import datetime


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
