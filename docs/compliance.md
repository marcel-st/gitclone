# Compliance & Controls

Lightweight control mapping for a single-user self-hosted archive. Not a formal certification —
a record of the guardrails the design commits to and where they are enforced.

## Applicable standards (aspirational)

- **ISO 27001** — information security controls (access, crypto, backup, logging).
- **OWASP ASVS 5.0** — application security verification for the orchestrator API.

## Control mapping

| Control area | Requirement | How it is met | Where |
|---|---|---|---|
| Secrets management | No secrets in code | All config via env; `.env` git-ignored; `.env.example` has keys only | `.env.example`, `.gitignore` |
| Credential least privilege | Discovery PAT read-only | GitHub PAT scoped to `repo` read + `read:org` | `accounts` app, operator docs |
| Encryption at rest | Tokens encrypted | PATs and push write-tokens stored Fernet-encrypted (`FIELD_ENCRYPTION_KEY`) | `accounts`, `destinations` models |
| Access control | No anonymous access | Forgejo `REQUIRE_SIGNIN_VIEW=true`; Django admin authed; Caddy sole entrypoint | Compose, Caddyfile |
| Strong auth | 2FA on admin | Enabled on the Forgejo admin account | Operator setup |
| Transport security | TLS everywhere public | Caddy automatic HTTPS; internal traffic on compose network | Caddyfile |
| Destructive-action control | Mirror-out gated | Push mirror opt-in per repo, confirmation + audit entry, diverging-history guard | `destinations` services |
| Auditability | Push-out actions logged | `audit_log` row per push / destructive action | `destinations` app |
| Resource abuse | API + disk limits | GitHub ETag/backoff; per-repo size cap; disk-usage pause threshold | `syncjobs`, env |
| Availability | Backups | Nightly `pg_dump` (both DBs) + Forgejo volume snapshot, off-VPS, 3-2-1 | Ops runbook |
| Container hardening | Non-root, healthchecks | `USER` directive; healthchecks on every service; named volumes | Compose, Dockerfiles |
| Legal | No unlawful redistribution | Private archive (sign-in required); upstream `LICENSE` preserved | Policy |

## Open items

- Off-VPS backup destination and restore-drill cadence to be decided by operator.
- LFS handling policy (skip vs. mirror) — default: skip repos over `MAX_REPO_SIZE_MB`, logged.
