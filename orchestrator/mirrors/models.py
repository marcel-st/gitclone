"""What to mirror (tracked_targets) and what is mirrored (mirrored_repos)."""
from django.db import models

from accounts.models import GithubAccount
from common.models import TimeStampedUUIDModel


class TrackedTarget(TimeStampedUUIDModel):
  """A declaration of what to mirror, resolved to repos during discovery."""

  class Kind(models.TextChoices):
    SELF_ALL = "self_all", "All of my repos"
    USER_ALL = "user_all", "All of a user's public repos"
    REPO = "repo", "A single repo"

  # Account whose PAT is used to discover/clone this target.
  account = models.ForeignKey(GithubAccount, on_delete=models.PROTECT, related_name="targets")
  kind = models.CharField(max_length=20, choices=Kind.choices)
  # For USER_ALL: the login to scan. For SELF_ALL: ignored.
  github_login = models.CharField(max_length=100, blank=True)
  # For REPO: "owner/name". Null otherwise.
  repo_full_name = models.CharField(max_length=255, blank=True)
  enabled = models.BooleanField(default=True)

  class Meta:
    db_table = "tracked_targets"
    ordering = ["kind", "github_login", "repo_full_name"]

  def __str__(self) -> str:
    return f"{self.kind}:{self.repo_full_name or self.github_login or self.account.login}"


class MirroredRepo(TimeStampedUUIDModel):
  """One repo under management, backed by a Forgejo pull mirror."""

  class SyncStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    OK = "ok", "OK"
    ERROR = "error", "Error"
    SKIPPED = "skipped", "Skipped"

  source_full_name = models.CharField(max_length=255, unique=True)  # owner/name on GitHub
  forgejo_owner = models.CharField(max_length=100)
  forgejo_repo_name = models.CharField(max_length=100)
  forgejo_repo_id = models.BigIntegerField(null=True, blank=True)
  is_private = models.BooleanField(default=False)
  size_bytes = models.BigIntegerField(default=0)
  last_sync_at = models.DateTimeField(null=True, blank=True)
  last_sync_status = models.CharField(
    max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING
  )
  last_error = models.TextField(blank=True)

  class Meta:
    db_table = "mirrored_repos"
    ordering = ["source_full_name"]

  def __str__(self) -> str:
    return self.source_full_name
