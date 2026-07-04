"""Discovery + mirror-in. Resolves tracked targets to repos and creates Forgejo pull mirrors."""
import logging

from django.conf import settings
from django.utils import timezone

from accounts import services as account_services
from accounts.models import GithubAccount
from common.exceptions import UpstreamError
from common.forgejo import ForgejoClient

from .models import MirroredRepo, TrackedTarget

logger = logging.getLogger(__name__)

_MB = 1024 * 1024


def _resolve_repos(target: TrackedTarget) -> list[dict]:
  """Return the GitHub repo objects a target expands to."""
  gh = account_services.client_for(target.account)
  if target.kind == TrackedTarget.Kind.SELF_ALL:
    return gh.list_self_repos()
  if target.kind == TrackedTarget.Kind.USER_ALL:
    return gh.list_user_repos(target.github_login)
  if target.kind == TrackedTarget.Kind.REPO:
    return [gh.get_repo(target.repo_full_name)]
  return []


def _over_size_cap(repo: dict) -> bool:
  cap = settings.MAX_REPO_SIZE_MB
  if cap <= 0:
    return False
  # GitHub reports repo size in KB.
  return repo.get("size", 0) * 1024 > cap * _MB


def _mirror_one(forgejo: ForgejoClient, account: GithubAccount, repo: dict) -> MirroredRepo:
  """Create (or fetch) the MirroredRepo row and its Forgejo pull mirror."""
  full_name = repo["full_name"]
  owner_login, repo_name = full_name.split("/", 1)

  record, _ = MirroredRepo.objects.get_or_create(
    source_full_name=full_name,
    defaults={
      "forgejo_owner": owner_login,
      "forgejo_repo_name": repo_name,
      "is_private": repo.get("private", False),
    },
  )

  if _over_size_cap(repo):
    record.last_sync_status = MirroredRepo.SyncStatus.SKIPPED
    record.last_error = "Repo exceeds MAX_REPO_SIZE_MB"
    record.save(update_fields=["last_sync_status", "last_error", "updated_at"])
    logger.info("Skipped %s (over size cap)", full_name)
    return record

  # Already provisioned in Forgejo: just trigger a refresh.
  if record.forgejo_repo_id:
    try:
      forgejo.sync_mirror(record.forgejo_owner, record.forgejo_repo_name)
      _mark_ok(record, repo)
    except UpstreamError as exc:
      _mark_error(record, str(exc))
    return record

  # New repo: create the pull mirror. Private sources need the PAT as auth_token.
  forgejo.ensure_org(owner_login)
  auth_token = account.pat_encrypted if repo.get("private") else None
  try:
    created = forgejo.create_pull_mirror(
      owner=owner_login,
      repo_name=repo_name,
      clone_url=repo["clone_url"],
      auth_token=auth_token,
    )
    record.forgejo_repo_id = created.get("id")
    _mark_ok(record, repo)
  except UpstreamError as exc:
    _mark_error(record, str(exc))
  return record


def _mark_ok(record: MirroredRepo, repo: dict) -> None:
  record.size_bytes = repo.get("size", 0) * 1024
  record.is_private = repo.get("private", False)
  record.last_sync_at = timezone.now()
  record.last_sync_status = MirroredRepo.SyncStatus.OK
  record.last_error = ""
  record.save()


def _mark_error(record: MirroredRepo, message: str) -> None:
  record.last_sync_at = timezone.now()
  record.last_sync_status = MirroredRepo.SyncStatus.ERROR
  record.last_error = message[:1000]
  record.save(update_fields=["last_sync_at", "last_sync_status", "last_error", "updated_at"])
  logger.warning("Mirror error: %s", message)


def run_discovery() -> dict[str, int]:
  """Scan all enabled targets and ensure every resolved repo has a Forgejo mirror.

  Returns a small summary. Safe to run repeatedly (idempotent per repo).
  """
  forgejo = ForgejoClient()
  summary = {"targets": 0, "repos_seen": 0, "errors": 0}

  targets = TrackedTarget.objects.filter(enabled=True, deleted_at__isnull=True)
  for target in targets.select_related("account"):
    summary["targets"] += 1
    try:
      repos = _resolve_repos(target)
    except UpstreamError as exc:
      logger.error("Target %s discovery failed: %s", target, exc)
      summary["errors"] += 1
      continue
    for repo in repos:
      summary["repos_seen"] += 1
      record = _mirror_one(forgejo, target.account, repo)
      if record.last_sync_status == MirroredRepo.SyncStatus.ERROR:
        summary["errors"] += 1

  logger.info("Discovery complete: %s", summary)
  return summary
