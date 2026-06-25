# Database migrations

Each `.sql` file here is a **migration** — one ordered step that changes the
Supabase database. They are applied automatically on push to `main` by the
GitHub Action in `.github/workflows/migrate.yml`.

## How to add a change

1. Create a new file named `NNN_short_description.sql`, where `NNN` is the next
   number in sequence (e.g. `001_create_tables.sql`, then `002_add_index.sql`).
   - The number before the first `_` sets the run order; the rest is just a label.
   - Numbers don't need leading zeros and can grow past 999 — they're sorted
     numerically (`sort -V`).
2. Put your SQL in the file.
3. Commit and push to `main`.

The Action runs only the files it hasn't run before (tracked in the
`public.schema_migrations` table) and applies them in numeric order.

## Tips

- Prefer re-runnable SQL where possible: `CREATE TABLE IF NOT EXISTS`,
  `CREATE OR REPLACE FUNCTION`, `CREATE INDEX IF NOT EXISTS`,
  `CREATE OR REPLACE TRIGGER`.
- Don't edit a file that has already been applied — it won't run again.
  Add a new numbered file instead.
