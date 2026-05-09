from celery import Celery
from app.config import settings

celery_app = Celery(
    "complyos_worker",
    broker=settings.REDIS_URL.replace("redis://", "rediss://" if "rediss" in settings.REDIS_URL else "redis://"), 
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    beat_schedule={
        'sentinel-monitor-every-hour': {
            'task': 'app.tasks.sentinel_tasks.monitor_circulars',
            'schedule': 3600.0, # 1 hour
        },
        'deadline-daily': {
             'task': 'app.tasks.deadline_tasks.send_reminders',
             'schedule': 28800.0 # 8 AM IST daily
        }
    }
)