"""Background scheduled jobs.

Uses APScheduler with BackgroundScheduler so the same process can serve both
HTTP and cron-style jobs (monthly bill generation, overdue sweep, reminders).
Disable via `ENABLE_SCHEDULERS=false` in `.env` if you only want HTTP.
"""
from __future__ import annotations

import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.base import session_scope
from app.services.billing_service import apply_late_fees_and_overdue

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def sweep_overdue_job() -> None:
    with session_scope() as db:
        n = apply_late_fees_and_overdue(db)
        logger.info("Sweep: %s bills marked overdue/updated", n)


def start_scheduler() -> None:
    global _scheduler
    if os.getenv("ENABLE_SCHEDULERS", "true").lower() not in ("1", "true", "yes", "on"):
        logger.info("Scheduler disabled by env")
        return
    if _scheduler is not None:
        return

    sched = BackgroundScheduler(timezone="UTC")
    # Daily sweep at 02:00 UTC
    sched.add_job(sweep_overdue_job, "cron", hour=2, minute=0, id="daily_sweep")
    sched.start()
    _scheduler = sched
    logger.info("Scheduler started")
