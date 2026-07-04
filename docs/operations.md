# Operations Runbook

Day-2 operations for the gitclone archive: backups, restore, monitoring, and routine tasks.

## First-boot setup

1. `cp .env.example .env` and fill every value. Generate secrets:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"                 # DJANGO_SECRET_KEY
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # FIELD_ENCRYPTION_KEY
   ```
2. `docker compose up -d`.
3. Open `https://<DOMAIN>/`, finish the Forgejo install wizard, create the admin account,
   then **enable 2FA** on it (Settings → Security).
4. In Forgejo, create an API token (Settings → Applications) and set `FORGEJO_ADMIN_TOKEN`
   in `.env`, then `docker compose up -d orchestrator scheduler` to reload.
5. Open `https://<DOMAIN>/app/` (dashboard) or `https://<DOMAIN>/admin/` (Django admin),
   add a GitHub account (read-only PAT), add a target, run discovery.

## Backups

`scripts/backup.sh` dumps both Postgres databases and the Forgejo data volume to a
timestamped directory, writes `SHA256SUMS`, and prunes to the last `BACKUP_RETENTION`
snapshots (default 14).

```bash
BACKUP_DIR=/srv/backups scripts/backup.sh
```

Cron (nightly at 03:00):

```cron
0 3 * * * cd /path/to/gitclone && BACKUP_DIR=/srv/backups scripts/backup.sh >> /var/log/gitclone-backup.log 2>&1
```

**3-2-1:** the script keeps local copies only. Sync `/srv/backups` to a second location
off the VPS (object storage / another host) — e.g. a following `rclone`/`rsync` step.

## Restore

`scripts/restore.sh <backup-dir>` is **destructive** — it verifies checksums, then overwrites
both databases and the Forgejo volume. It prompts for a typed `RESTORE` confirmation.

```bash
scripts/restore.sh /srv/backups/20260704_030000
```

Run a **restore drill** quarterly against a throwaway environment to confirm backups are valid.

## Monitoring

`scripts/monitor.sh` reports container health and Forgejo `/data` disk usage, exiting
non-zero if any service is unhealthy or disk usage is at/over `DISK_PAUSE_THRESHOLD_PERCENT`.

Cron with mail-on-failure (cron mails any output; the script is quiet-ish on success):

```cron
*/15 * * * * cd /path/to/gitclone && scripts/monitor.sh || echo "gitclone monitor FAILED"
```

The healthchecks defined per service in `docker-compose.yml` also let `docker compose ps`
and orchestration restarts react to failures automatically.

## Routine tasks

| Task | How |
|------|-----|
| Force a discovery run now | Dashboard → Targets → "run discovery", or `docker compose exec orchestrator python manage.py discover` |
| Add a repo to mirror | Dashboard → Targets → add (`repo` = `owner/name`) |
| Push a repo out | Dashboard → Push links → link repo↔destination → "push" (confirms first) |
| Rotate a PAT / token | Update via dashboard; old value is overwritten (encrypted at rest) |
| Inspect audit trail | Dashboard → Audit, or Django admin → Audit logs |

## Capacity

- Watch `/data` usage via `monitor.sh`. When it approaches the threshold, expand the
  `forgejo_data` volume's underlying disk before it fills.
- `MAX_REPO_SIZE_MB` skips oversized repos at discovery (logged as `skipped`, not dropped
  silently). Raise it or handle LFS explicitly if you need large repos.
