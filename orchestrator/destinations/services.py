"""Mirror-out logic. Push is destructive (force-updates the remote) so it is gated."""
import logging

from django.utils import timezone

from common.exceptions import GuardrailError
from common.forgejo import ForgejoClient

from .models import AuditLog, PushMirrorLink

logger = logging.getLogger(__name__)


def _record_url(link: PushMirrorLink) -> str:
  """Full remote URL for this repo on the destination."""
  base = link.destination.remote_url.rstrip("/")
  return f"{base}/{link.repo.forgejo_repo_name}.git"


def push_now(link: PushMirrorLink, actor: str, confirmed: bool) -> None:
  """Configure (if needed) and trigger a push mirror for one repo→destination link.

  Guardrails:
    - The destination must be enabled.
    - If the link requires confirmation, `confirmed` must be True.
    - Every push writes an audit entry.
  """
  if not link.destination.enabled:
    raise GuardrailError("Destination is disabled.")
  if link.require_confirmation and not confirmed:
    raise GuardrailError(
      "Push requires explicit confirmation (it force-updates the remote)."
    )

  forgejo = ForgejoClient()
  owner, repo_name = link.repo.forgejo_owner, link.repo.forgejo_repo_name

  # Create the Forgejo push mirror once; afterwards we only trigger syncs.
  if not link.forgejo_push_mirror_id:
    created = forgejo.add_push_mirror(
      owner=owner,
      repo_name=repo_name,
      remote_url=_record_url(link),
      remote_username=link.destination.remote_username,
      remote_token=link.destination.write_token_encrypted,
    )
    link.forgejo_push_mirror_id = created.get("id")

  forgejo.sync_push_mirror(owner, repo_name)
  link.last_pushed_at = timezone.now()
  link.save(update_fields=["forgejo_push_mirror_id", "last_pushed_at", "updated_at"])

  AuditLog.objects.create(
    actor=actor,
    action="push_mirror",
    target=str(link),
    detail=f"Pushed {link.repo.source_full_name} to {link.destination.name}",
  )
  logger.info("Push mirror triggered: %s by %s", link, actor)
