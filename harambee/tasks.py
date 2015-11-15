from celery import task
from rolefit.communication import save_stats
from harambee.metrics import create_json_stats


@task(bind=True)
def send_metrics():
    stats = create_json_stats()
    save_stats(stats)