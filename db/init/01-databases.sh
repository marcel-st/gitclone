#!/bin/bash
# Creates the two application databases and their owners on first Postgres init.
# Runs as the Postgres superuser via the official image's /docker-entrypoint-initdb.d hook.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-SQL
  CREATE USER ${FORGEJO_DB_USER} WITH PASSWORD '${FORGEJO_DB_PASSWORD}';
  CREATE DATABASE ${FORGEJO_DB_NAME} OWNER ${FORGEJO_DB_USER};

  CREATE USER ${ORCHESTRATOR_DB_USER} WITH PASSWORD '${ORCHESTRATOR_DB_PASSWORD}';
  CREATE DATABASE ${ORCHESTRATOR_DB_NAME} OWNER ${ORCHESTRATOR_DB_USER};
SQL
