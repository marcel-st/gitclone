"""Mirror-out remotes, per-repo push links, and the audit log."""
from django.db import models

from common.fields import EncryptedTextField
from common.models import TimeStampedUUIDModel
from mirrors.models import MirroredRepo


class PushDestination(TimeStampedUUIDModel):
  """An external forge to push a mirror out to."""

  class Type(models.TextChoices):
    GITHUB = "github", "GitHub"
    GITLAB = "gitlab", "GitLab"
    GITEA = "gitea", "Gitea"

  name = models.CharField(max_length=100, unique=True)
  type = models.CharField(max_length=20, choices=Type.choices)
  # Base remote URL, e.g. https://github.com/owner (repo appended per link).
  remote_url = models.CharField(max_length=500)
  remote_username = models.CharField(max_length=100)
  # Write-scoped token. Encrypted at rest; decrypted only at push time.
  write_token_encrypted = EncryptedTextField()
  enabled = models.BooleanField(default=True)

  class Meta:
    db_table = "push_destinations"
    ordering = ["name"]

  def __str__(self) -> str:
    return self.name


class PushMirrorLink(TimeStampedUUIDModel):
  """Opt-in binding of one mirrored repo to one push destination."""

  repo = models.ForeignKey(MirroredRepo, on_delete=models.CASCADE, related_name="push_links")
  destination = models.ForeignKey(
    PushDestination, on_delete=models.CASCADE, related_name="push_links"
  )
  forgejo_push_mirror_id = models.BigIntegerField(null=True, blank=True)
  # Guardrail: a push must be explicitly confirmed unless this is cleared.
  require_confirmation = models.BooleanField(default=True)
  last_pushed_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = "push_mirror_links"
    unique_together = [("repo", "destination")]

  def __str__(self) -> str:
    return f"{self.repo.source_full_name} -> {self.destination.name}"


class AuditLog(TimeStampedUUIDModel):
  """Append-only record of push-out and other destructive actions."""

  actor = models.CharField(max_length=150)
  action = models.CharField(max_length=100)
  target = models.CharField(max_length=500)
  detail = models.TextField(blank=True)

  class Meta:
    db_table = "audit_log"
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return f"{self.action} {self.target}"
