"""Business logic for GitHub accounts. Views delegate here."""
from .github import GithubClient
from .models import GithubAccount


def client_for(account: GithubAccount) -> GithubClient:
  """Build an authenticated GitHub client for an account (decrypts the PAT in memory)."""
  return GithubClient(pat=account.pat_encrypted)


def active_accounts() -> list[GithubAccount]:
  return list(GithubAccount.objects.filter(enabled=True, deleted_at__isnull=True))


def self_account() -> GithubAccount | None:
  return GithubAccount.objects.filter(
    is_self=True, enabled=True, deleted_at__isnull=True
  ).first()
