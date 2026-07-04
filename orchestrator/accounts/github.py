"""GitHub REST client for repo discovery. Handles pagination and rate limits."""
import time

import requests

from common.exceptions import UpstreamError

_API = "https://api.github.com"
_TIMEOUT = 30
_MAX_RETRIES = 3


class GithubClient:
  """Lists repositories for the authenticated user or an arbitrary user."""

  def __init__(self, pat: str) -> None:
    self._pat = pat

  def _headers(self) -> dict[str, str]:
    return {
      "Authorization": f"Bearer {self._pat}",
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    }

  def _get(self, url: str, params: dict | None = None) -> requests.Response:
    for attempt in range(_MAX_RETRIES):
      resp = requests.get(url, headers=self._headers(), params=params, timeout=_TIMEOUT)
      # Primary rate limit: wait until reset, then retry.
      if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
        wait = max(reset - int(time.time()), 1)
        if attempt < _MAX_RETRIES - 1:
          time.sleep(min(wait, 60))
          continue
        raise UpstreamError("GitHub rate limit exhausted.")
      if resp.status_code >= 500 and attempt < _MAX_RETRIES - 1:
        time.sleep(2 ** attempt)
        continue
      return resp
    raise UpstreamError("GitHub request failed after retries.")

  def _paginate(self, url: str, params: dict) -> list[dict]:
    results: list[dict] = []
    while url:
      resp = self._get(url, params)
      if resp.status_code != 200:
        raise UpstreamError(f"GitHub {resp.status_code}: {resp.text[:200]}")
      results.extend(resp.json())
      url = resp.links.get("next", {}).get("url", "")
      params = {}  # subsequent page URLs already carry query params
    return results

  def list_self_repos(self) -> list[dict]:
    """All repos the token owner can access, including private and org repos."""
    return self._paginate(
      f"{_API}/user/repos",
      {"per_page": 100, "affiliation": "owner", "sort": "full_name"},
    )

  def list_user_repos(self, login: str) -> list[dict]:
    """Public repos of another user."""
    return self._paginate(f"{_API}/users/{login}/repos", {"per_page": 100, "sort": "full_name"})

  def get_repo(self, full_name: str) -> dict:
    """A single repo by `owner/name`."""
    resp = self._get(f"{_API}/repos/{full_name}")
    if resp.status_code == 404:
      raise UpstreamError(f"GitHub repo not found: {full_name}")
    if resp.status_code != 200:
      raise UpstreamError(f"GitHub {resp.status_code}: {resp.text[:200]}")
    return resp.json()
