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
from app.services.billing_service import apply_late_fees_and_overdue, generate_monthly_bills

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def sweep_overdue_job() -> None:
    with session_scope() as db:
        n = apply_late_fees_and_overdue(db)
        logger.info("Sweep: %s bills marked overdue/updated", n)


def monthly_bills_job() -> None:
    """Generate bills for every society once a month (idempotent due to bill_number)."""
    from app.models.society import Society
    with session_scope() as db:
        from app.models.bill import Bill
        from sqlalchemy import select
        from datetime import datetime, date

        # Skip if bills were already generated this calendar month
        already = db.execute(select(Bill).where(
            Bill.created_at >= datetime(date.today().year, date.today().month, 1)
        )).first()
        if already:
            logger.info("Monthly bills already exist for this month; skipping.")
            return
        societies = db.execute(select(Society)).scalars().all()
        for s in societies:
            generate_monthly_bills(db, s.id)
        logger.info("Monthly bills generated for %s societies", len(societies))


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
    # Monthly on the 1st at 03:00 UTC
    sched.add_job(monthly_bills_job, "cron", day=1, hour=3, minute=0, id="monthly_bills")
    sched.start()
    _scheduler = sched
    logger.info("Scheduler started")
