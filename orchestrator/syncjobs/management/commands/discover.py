"""One-shot discovery run. Usable from cron, CI, or manually."""
from django.core.management.base import BaseCommand

from mirrors.services import run_discovery


class Command(BaseCommand):
  help = "Scan all enabled tracked targets and ensure Forgejo pull mirrors exist."

  def handle(self, *args, **options) -> None:
    summary = run_discovery()
    self.stdout.write(self.style.SUCCESS(f"Discovery complete: {summary}"))
