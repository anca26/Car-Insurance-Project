# core/jobs.py
from django.db import transaction
from django.utils import timezone
from insurance.models import InsurancePolicy

try:
    import structlog
    log = structlog.get_logger()
except Exception:
    import logging
    log = logging.getLogger(__name__)

def log_today_expired_policies():
    """
    Run every 10 minutes. Only act if 'now' is within [today 00:00, today 01:00)
    in server local time. Find policies with end_date == today and not logged yet.
    Log once and set logged_expiry_at = now() for idempotency.
    """
    now = timezone.localtime()  # local time (respects TIME_ZONE + USE_TZ)
    today = now.date()

    # Window: [today 00:00, today 01:00)
    window_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    window_end   = window_start + timezone.timedelta(hours=1)

    if not (window_start <= now < window_end):
        # Outside the window; do nothing to satisfy the spec
        log.debug("expiry_job_outside_window", now=now.isoformat())
        return

    # Idempotent logging: only pick where not yet logged
    # Use a transaction + SELECT FOR UPDATE SKIP LOCKED (safe across schedulers)
    with transaction.atomic():
        # SQLite ignores select_for_update; still safe in single-process APScheduler.
        candidates = (InsurancePolicy.objects
                      .select_for_update()
                      .filter(end_date=today, logged_expiry_at__isnull=True))

        count = 0
        for p in candidates:
            log.info("policy_expired",
                     policy_id=p.id, car_id=p.car_id, end_date=p.end_date.isoformat())
            p.logged_expiry_at = timezone.now()
            p.save(update_fields=["logged_expiry_at"])
            count += 1

        log.info("expiry_job_done", processed=count, date=today.isoformat())
