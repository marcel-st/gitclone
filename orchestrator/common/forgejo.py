"""Thin Forgejo API client. Only the calls the orchestrator needs."""
import requests
from django.conf import settings

from common.exceptions import UpstreamError

_TIMEOUT = 30


class ForgejoClient:
  """Wraps the Forgejo REST API using the admin token."""

  def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
    self.base_url = (base_url or settings.FORGEJO_API_URL).rstrip("/")
    self.token = token or settings.FORGEJO_ADMIN_TOKEN

  def _headers(self) -> dict[str, str]:
    return {
      "Authorization": f"token {self.token}",
      "Content-Type": "application/json",
    }

  def _request(self, method: str, path: str, **kwargs) -> requests.Response:
    url = f"{self.base_url}/api/v1{path}"
    try:
      resp = requests.request(method, url, headers=self._headers(), timeout=_TIMEOUT, **kwargs)
    except requests.RequestException as exc:
      raise UpstreamError(f"Forgejo request failed: {exc}") from exc
    if resp.status_code >= 500:
      raise UpstreamError(f"Forgejo returned {resp.status_code}: {resp.text[:200]}")
    return resp

  def ensure_org(self, org_name: str) -> None:
    """Create an org to hold a tracked user's mirrors, if it does not exist."""
    resp = self._request("GET", f"/orgs/{org_name}")
    if resp.status_code == 200:
      return
    create = self._request("POST", "/orgs", json={"username": org_name, "visibility": "private"})
    if create.status_code not in (201, 422):  # 422 = already exists
      raise UpstreamError(f"Could not create org {org_name}: {create.text[:200]}")

  def create_pull_mirror(
    self, owner: str, repo_name: str, clone_url: str, auth_token: str | None
  ) -> dict:
    """Create a private pull-mirror repo under `owner` cloning from `clone_url`."""
    payload = {
      "repo_name": repo_name,
      "repo_owner": owner,
      "clone_addr": clone_url,
      "mirror": True,
      "private": True,
      "service": "git",
    }
    if auth_token:
      payload["auth_token"] = auth_token  # for private source repos
    resp = self._request("POST", "/repos/migrate", json=payload)
    if resp.status_code == 201:
      return resp.json()
    if resp.status_code == 409:
      raise UpstreamError(f"Mirror already exists: {owner}/{repo_name}")
    raise UpstreamError(f"Migrate failed ({resp.status_code}): {resp.text[:200]}")

  def sync_mirror(self, owner: str, repo_name: str) -> None:
    """Force an immediate pull-mirror refresh."""
    self._request("POST", f"/repos/{owner}/{repo_name}/mirror-sync")

  def add_push_mirror(
    self, owner: str, repo_name: str, remote_url: str, remote_username: str, remote_token: str
  ) -> dict:
    """Configure a push mirror on an existing repo. Push is manual-triggered, not periodic."""
    payload = {
      "remote_address": remote_url,
      "remote_username": remote_username,
      "remote_password": remote_token,
      "sync_on_commit": False,
      "interval": "0",  # no automatic interval; we trigger explicitly
    }
    resp = self._request(
      "POST", f"/repos/{owner}/{repo_name}/push_mirrors", json=payload
    )
    if resp.status_code in (200, 201):
      return resp.json()
    raise UpstreamError(f"Add push mirror failed ({resp.status_code}): {resp.text[:200]}")

  def sync_push_mirror(self, owner: str, repo_name: str) -> None:
    """Trigger a push-mirror run now (force-updates the remote)."""
    self._request("POST", f"/repos/{owner}/{repo_name}/push_mirrors-sync")
