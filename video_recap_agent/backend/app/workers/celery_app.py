from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "video_recap",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=35 * 60,      # 35 min hard limit
    task_soft_time_limit=30 * 60,  # 30 min soft limit
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.process_recap_job": {"queue": "processing"},
        "app.workers.tasks.cleanup_expired_files": {"queue": "maintenance"},
    },
    beat_schedule={
        "cleanup-expired-files": {
            "task": "app.workers.tasks.cleanup_expired_files",
            "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
        },
    },
)

celery_app.autodiscover_tasks(["app.workers"])
