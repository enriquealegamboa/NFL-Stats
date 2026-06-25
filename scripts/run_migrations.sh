#!/usr/bin/env bash
#
# Applies every *.sql file in database/migrations/ that has not been applied yet,
# in numeric/alphabetical order. Each file is run once and recorded in the
# public.schema_migrations table so it is never run again.
#
# Requires the DATABASE_URL environment variable (a Postgres connection string).

set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is not set}"

MIGRATIONS_DIR="database/migrations"

# 1. Make sure the tracking table exists.
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q <<'SQL'
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    filename   text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
SQL

# 2. Walk the migration files in numeric order and apply the new ones.
#    `sort -V` (version sort) orders them numerically, so 999 comes before 1000
#    (a plain `sort` is alphabetical and would put 1000 before 999).
shopt -s nullglob
for file in $(ls "$MIGRATIONS_DIR"/*.sql | sort -V); do
    name="$(basename "$file")"

    already_applied="$(psql "$DATABASE_URL" -tAc \
        "SELECT 1 FROM public.schema_migrations WHERE filename = '$name'")"

    if [ "$already_applied" = "1" ]; then
        echo "skip   $name (already applied)"
        continue
    fi

    echo "apply  $name"
    # Run the file and record it in a SINGLE transaction: if the SQL fails,
    # ON_ERROR_STOP aborts and the whole thing (including the record) rolls back.
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 --single-transaction \
        -f "$file" \
        -c "INSERT INTO public.schema_migrations (filename) VALUES ('$name');"
    echo "done   $name"
done

echo "All migrations up to date."
