# gitclone — Git Mirror & Archive Service

Self-hosted archive that automatically mirrors your GitHub repositories (and hand-picked
repos from other users) for safekeeping. Browse behind a login, clone over git, and push
mirrors back out to GitHub / GitLab / Gitea on demand.

## How it works

- **Forgejo** is the git engine: storage, web UI (sign-in required), git-over-HTTPS/SSH,
  native pull mirrors (mirror *in*) and push mirrors (mirror *out*).
- **Django orchestrator** discovers repos via the GitHub API and configures Forgejo mirrors
  through Forgejo's API. It owns scheduling, the admin dashboard, and push-out control.
- **Caddy** is the only public entrypoint (TLS). **Postgres** backs both services.

See `docs/architecture.md` for the full design and `docs/compliance.md` for the control mapping.

## Run (local dev)

```bash
cp .env.example .env      # fill in the values
docker compose up -d
```

Services:

| URL                         | What                                   |
|-----------------------------|----------------------------------------|
| `https://<DOMAIN>/`         | Forgejo — browse archive, git endpoint |
| `https://<DOMAIN>/app/`     | React dashboard (targets, repos, push) |
| `https://<DOMAIN>/admin/`   | Django admin (raw data + audit log)    |

First boot and day-2 operations (backups, restore, monitoring) are documented in
`docs/operations.md`. In short: complete the Forgejo install wizard, create the admin
account, enable 2FA, then create a Forgejo API token and put it in `.env` as
`FORGEJO_ADMIN_TOKEN`.

## Environment

All configuration is via environment variables. See `.env.example` for the full list of keys.
Never commit `.env` or any real secret.

## Guardrails

- GitHub discovery PAT is **read-only**. Push-out write tokens are separate and encrypted at rest.
- Mirror-out is **manual and opt-in per repo** — it force-updates the remote and is treated as destructive.
- No anonymous browsing (`REQUIRE_SIGNIN_VIEW=true`). Containers run non-root. Nightly backups.

This is a **private archive**. Respect upstream licenses; do not redistribute mirrored content.
