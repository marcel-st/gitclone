# Architecture

Status: accepted · Date: 2026-07-03

## Context

Marcel wants a self-hosted archive that automatically mirrors (1) all of his own GitHub
repositories and (2) hand-picked repositories from other GitHub users, for safekeeping.
The archive must be browsable behind a login, retrievable via `git clone`, and able to push
its contents back out to a GitHub / GitLab / Gitea instance on demand.

## Decision

Do not rebuild git hosting. Use **Forgejo** (a maintained Gitea fork) as the git engine and
put a thin **Django + DRF orchestrator** on top.

- Forgejo already provides git storage, a web UI behind auth, git-over-HTTPS/SSH, native
  **pull mirrors** (mirror in from GitHub) and native **push mirrors** (mirror out to another
  forge). Rebuilding any of that in Django would be large and add security surface.
- The orchestrator does only what Forgejo cannot: discover repos via the GitHub API, decide
  what to mirror, create/refresh mirrors through the Forgejo API, schedule discovery, and
  gate push-out actions.

Rejected alternative: pure custom Django + raw git (git-http-backend, custom UI/auth). Full
control but reimplements everything Forgejo gives for free — violates "don't over-engineer".

## System

```
                    ┌─────────────────────────────────────────────┐
                    │              Reverse proxy (Caddy)           │
                    │        TLS, single entrypoint, auth gate     │
                    └───────────────┬─────────────────┬───────────┘
                                    │                 │
                    ┌───────────────▼──────┐   ┌──────▼──────────────┐
   GitHub API ─────▶│  Django orchestrator │   │      Forgejo        │◀── git clone/push
  (discovery,       │  (DRF + admin dash)  │──▶│  web UI + git server │    (HTTPS/SSH)
   private via PAT) │  scheduler, push ctl │   │  pull & push mirrors │
                    └──────────┬───────────┘   └──────────┬──────────┘
                               │                          │
                    ┌──────────▼───────────┐   ┌──────────▼──────────┐
                    │  Postgres: orchestr. │   │ Postgres: forgejo   │
                    └──────────────────────┘   │ Volume: repo data   │
                                               └─────────────────────┘
```

### Components

| Service        | Role                                                                 |
|----------------|----------------------------------------------------------------------|
| `caddy`        | Reverse proxy, automatic TLS, only public surface. `/`→Forgejo, `/admin/`→Django. |
| `forgejo`      | Git engine. Bare mirrors. `REQUIRE_SIGNIN_VIEW=true`, 2FA admin, push mirrors. |
| `orchestrator` | Django + DRF + scheduler. GitHub discovery, Forgejo API config, dashboard.  |
| `db`           | Postgres 16, two databases: `forgejo`, `orchestrator`.               |

## Requirement → mechanism

| Requirement | Mechanism |
|---|---|
| Mirror all my repos | Django lists repos via GitHub PAT, creates each as a Forgejo pull mirror. New repos auto-detected on schedule. |
| Mirror specific other users' repos | Web UI adds a `TrackedTarget`; same pull-mirror path. |
| Browse behind credentials | Forgejo web UI, sign-in required. Django dashboard authed. |
| Retrieve via git | `git clone https://forge.domain/owner/repo.git` with a Forgejo token, or SSH key. |
| Push out to GitHub/GitLab/Gitea | Forgejo push mirror per repo → target remote + write token, triggered manually. |

## Data model (orchestrator)

All tables carry `id UUID PK`, `created_at`, `updated_at`, `deleted_at` (soft delete).

- `github_accounts` — PAT-backed discovery identity. `login`, `pat_encrypted`, `is_self`.
- `tracked_targets` — what to mirror. `kind` (`self_all`|`user_all`|`repo`), `github_login`, `repo_full_name?`, `enabled`.
- `mirrored_repos` — one row per managed repo. `source_full_name`, `forgejo_repo_id`, `last_sync_at`, `last_sync_status`, `size_bytes`, `is_private`.
- `push_destinations` — mirror-out remotes. `type`, `remote_url`, `write_token_encrypted`, `enabled`.
- `push_mirror_links` — join repos↔destinations. `forgejo_push_mirror_id`, `require_confirmation`, `last_pushed_at`.
- `audit_log` — every push-out / destructive action. `actor`, `action`, `target`, `detail`, `timestamp`.

## Sync flows

**Discovery + mirror-in** (scheduled every `DISCOVERY_INTERVAL_HOURS`, plus manual trigger):
list repos per enabled target via GitHub API (ETag caching), diff against `mirrored_repos`,
create pull mirrors for new repos via Forgejo migrate API (`mirror=true`), record status/size.

**Mirror-out** (manual, explicit): user picks a repo + destination; Django creates/triggers a
Forgejo push mirror and writes an `audit_log` row. Never automatic — push mirroring force-updates
the remote and is treated as destructive.

## Consequences

- Minimal custom code; most capability is Forgejo configuration.
- Two web surfaces (Forgejo browse, Django admin) both behind auth via Caddy.
- Forgejo's own mirror scheduler refreshes existing pull mirrors; Django only handles
  discovery of *new* repos and push-out control.
