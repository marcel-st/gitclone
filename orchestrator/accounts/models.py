"""GitHub identities used for repo discovery."""
from django.db import models

from common.fields import EncryptedTextField
from common.models import TimeStampedUUIDModel


class GithubAccount(TimeStampedUUIDModel):
  """A GitHub login plus a read-only PAT used to discover and clone its repos.

  Exactly one account should have is_self=True — it represents the owner and its
  repos are all mirrored (kind=self_all target).
  """

  login = models.CharField(max_length=100, unique=True)
  # Read-only scopes only (repo:read, read:org). Encrypted at rest.
  pat_encrypted = EncryptedTextField()
  is_self = models.BooleanField(default=False)
  enabled = models.BooleanField(default=True)

  class Meta:
    db_table = "github_accounts"
    ordering = ["login"]

  def __str__(self) -> str:
    return self.login
