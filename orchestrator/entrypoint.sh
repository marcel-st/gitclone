#!/bin/sh
# Prepare the app on container start, then exec the given command (server/scheduler).
set -e

echo "[entrypoint] applying migrations"
python manage.py makemigrations accounts mirrors destinations syncjobs --noinput
python manage.py migrate --noinput

echo "[entrypoint] collecting static"
python manage.py collectstatic --noinput || true

# Bootstrap the admin superuser if credentials are provided (dev convenience).
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
  echo "[entrypoint] ensuring superuser ${DJANGO_SUPERUSER_USERNAME}"
  python manage.py createsuperuser --noinput || true
fi

exec "$@"
