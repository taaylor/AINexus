#!/bin/sh

set -eu

export POSTGRES_EXPORTER_USER="${POSTGRES_EXPORTER_USER:-postgres_exporter}"
export POSTGRES_EXPORTER_PASSWORD="${POSTGRES_EXPORTER_PASSWORD:-$POSTGRES_PASSWORD}"

psql \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 <<'SQL'
\getenv exporter_user POSTGRES_EXPORTER_USER
\getenv exporter_password POSTGRES_EXPORTER_PASSWORD

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'exporter_user', :'exporter_password')
WHERE NOT EXISTS (
  SELECT 1
  FROM pg_roles
  WHERE rolname = :'exporter_user'
)
\gexec

SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'exporter_user', :'exporter_password')
\gexec

SELECT format('GRANT pg_monitor TO %I', :'exporter_user')
\gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', current_database(), :'exporter_user')
\gexec
SQL
