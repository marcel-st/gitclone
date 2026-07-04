# ─── base: shared Python layer with dependencies ─────────────────────────────
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl git \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user matching the compose `user: 1000:1000`.
RUN useradd --uid 1000 --create-home appuser

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# ─── dev: live-mounted source, runserver ─────────────────────────────────────
FROM base AS dev
USER appuser
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ─── runtime: baked source, gunicorn ─────────────────────────────────────────
FROM base AS runtime
COPY --chown=appuser:appuser . .
USER appuser
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
