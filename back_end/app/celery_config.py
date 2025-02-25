from datetime import timedelta

from celery import Celery

from app import config

celery = Celery(broker=config.REDIS_ENDPOINT)

celery.conf.beat_schedule = {
    "reconcile-every-10-minutes": {
        "task": "app.ct_core.reconcile_document_processing",
        "schedule": timedelta(minutes=10),
        "options": {"priority": 0},
    },
}
