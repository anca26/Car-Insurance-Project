# core/scheduler.py
import os
from django.conf import settings

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .jobs import log_today_expired_policies

_scheduler = None

def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    if not settings.SCHEDULER_ENABLED:
        return None

    # Avoid double-start under Django autoreload in DEBUG
    if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
        return None

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.start()
    scheduler.add_job(
        log_today_expired_policies,
        trigger=IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
        id="log_expired_policies_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler = scheduler
    return scheduler
