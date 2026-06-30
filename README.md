# NFL Stats

A full-stack NFL data platform: ETL from the ESPN API into Supabase, a Java/Spring Boot REST API on Railway, and a Next.js web app on Vercel.

The goal is a **production-style stack** that can power analytics, dashboards, or sports applications using real NFL data.

---

## Architecture

```
ESPN API ──► data_pipeline (Python) ──► Supabase (Postgres)
                                              ▲
                                              │
                       backend (Java/Spring Boot, Railway)
                                              ▲
                                              │
                          frontend (Next.js, Vercel)
```

---

## Repo layout

| Folder | Purpose | Stack | Hosted on |
| :--- | :--- | :--- | :--- |
| [`frontend/`](frontend) | Web app | Next.js (App Router) + TypeScript | Vercel |
| [`backend/`](backend) | REST API | Java + Spring Boot (Maven) | Railway |
| [`data_pipeline/`](data_pipeline) | ETL: ESPN API → Supabase | Python (`requests`, `pandas`, `supabase`) | Run on demand |
| [`database/`](database) | SQL migrations (schema, functions, triggers, indexes) | PostgreSQL | Supabase |

---

## Database

Postgres on Supabase. Schema designed from an EER model. Core tables:

| Table | Description |
| :--- | :--- |
| `team` | NFL team information |
| `player` | Player roster data |
| `game` | NFL games by season and week |
| `season` | NFL seasons |
| `season_team_stats` | Aggregated team statistics for a season |
| `season_player_stats` | Player season totals (detail split by category across `season_player_*` tables) |
| `game_team_stats` | Team statistics for a single game |
| `game_player_stats` | Player appearances in a game (detail split by category across `game_player_*` tables) |

Lookup/support tables: `conference`, `division`, `position`, `player_position`, `roster`.

### Stat detail tables (downstream of the `*_player_stats` parents)

Each parent row fans out into per-category detail tables (foreign-keyed back to the parent):

**Season player stats** → `season_player_stats`
`season_player_passing_stats`, `season_player_rushing_stats`, `season_player_receiving_stats`, `season_player_defense_stats`, `season_player_scoring_stats`, `season_player_kicking_stats`, `season_player_punting_stats`, `season_player_return_stats`

**Game player stats** → `game_player_stats`
`game_player_passing_stats`, `game_player_rushing_stats`, `game_player_receiving_stats`, `game_player_defense_stats`, `game_player_interception_stats`, `game_player_fumble_stats`, `game_player_kicking_stats`, `game_player_punting_stats`, `game_player_return_stats`

Migrations live under [`database/migrations/`](database/migrations).

---

## Running locally

### 1. Backend (Spring Boot on Railway)

Requires a JDK 21 on your PATH (e.g. `winget install Microsoft.OpenJDK.21`). Maven is not
required — the project ships the Maven Wrapper (`mvnw`), which downloads Maven on first use.

```bash
cd backend
cp .env.example .env   # optional until DB access is enabled (see backend/README.md)
./mvnw spring-boot:run # http://localhost:8080  (Windows PowerShell: .\mvnw.cmd spring-boot:run)
```

Run the tests with `./mvnw test`. See [`backend/README.md`](backend/README.md) for details.

### 2. Frontend (Next.js on Vercel)

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
npm run dev                  # http://localhost:3000
```

### 3. Data pipeline (ETL)

Python scripts that pull from the ESPN API and upsert into Supabase. Install
dependencies and set your Supabase credentials as environment variables:

```bash
cd data_pipeline
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

export SUPABASE_URL="https://<project>.supabase.co"
export SUPABASE_SECRET_KEY="<service_role / secret key>"   # bypasses RLS for writes
```

Entry-point scripts (run from the `data_pipeline/` folder):

| Script | What it does | When to run |
| :--- | :--- | :--- |
| `team_info.py` | Loads the 32 teams from `teams_df.csv` | Once, at setup |
| `pull_team_season_data.py` | Backfills team-season stats for past years (2011–) | On demand |
| `pull_weekly.py` | Auto-detects the current NFL week and pulls that week's games, box scores, rosters, and player season stats | Automated weekly (below) |

`pipeline_utils.py` holds shared helpers and isn't run directly.

**Order on a fresh database:** apply `database/migrations/` first, then run
`team_info.py`, then the pulls.

#### Automated weekly pull

`pull_weekly.py` runs on a schedule via GitHub Actions
([`.github/workflows/weekly-pull.yml`](.github/workflows/weekly-pull.yml)) —
Tuesdays 12:00 UTC, plus a manual "Run workflow" button. It only pulls completed
games and no-ops in the off-season, so it's safe to run year-round. Add the
`SUPABASE_URL` and `SUPABASE_SECRET_KEY` repository secrets so it can connect.

---

## Deployment

- **Frontend** — Vercel auto-detects Next.js. Set project root to `frontend/` and `NEXT_PUBLIC_API_BASE_URL` to the Railway URL.
- **Backend** — Railway uses `backend/railway.json` (Nixpacks auto-detects the Maven project and runs `java -jar target/app.jar`). Set `CORS_ORIGIN` (your Vercel URL), and — once DB access is enabled — `SUPABASE_DB_URL`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`.
- **Database** — Apply files in `database/migrations/` to Supabase in order.

---

## Author

Enrique Gamboa — Backend Development | Data Engineering | Database Design
