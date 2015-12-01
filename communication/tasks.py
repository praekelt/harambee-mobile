from celery import task
from communication.models import Sms
from rolefit.communication import send_sms
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
