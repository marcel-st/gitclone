"""Long-running scheduler process. Runs discovery on a fixed interval."""
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand

from mirrors.services import run_discovery

logger = logging.getLogger(__name__)


class Command(BaseCommand):
  help = "Run the periodic discovery scheduler (blocking)."

  def handle(self, *args, **options) -> None:
    hours = settings.DISCOVERY_INTERVAL_HOURS
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_job(
      _safe_discovery,
      trigger="interval",
      hours=hours,
      # Run once shortly after boot instead of waiting a full interval.
      next_run_time=None,
      id="discovery",
      max_instances=1,
      coalesce=True,
    )
    logger.info("Scheduler started; discovery every %s h", hours)
    scheduler.start()


def _safe_discovery() -> None:
  try:
    run_discovery()
  except Exception:  # scheduler must survive a failed run
    logger.exception("Scheduled discovery failed")
