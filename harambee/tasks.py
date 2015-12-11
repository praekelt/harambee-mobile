from djcelery import celery
from rolefit.communication import save_stats
from harambee.metrics import create_json_stats


@celery.task(bind=True)
def send_metrics(self):
    stats = create_json_stats()
    save_stats(stats)
