from celery import task
from rolefit.communication import save_stats


@task(bind=True)
def send_metrics(stats):
    save_stats(stats)