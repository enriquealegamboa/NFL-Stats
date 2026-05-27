# NFL Stats

A full-stack NFL data platform: ETL from the ESPN API into Supabase, a Node/Express REST API on Railway, and a Next.js web app on Vercel.

The goal is a **production-style stack** that can power analytics, dashboards, or sports applications using real NFL data.

---

## Architecture

```
ESPN API ──► data_pipeline (Python) ──► Supabase (Postgres)
                                              ▲
                                              │
                          backend (Express/TS, Railway)
                                              ▲
                                              │
                          frontend (Next.js, Vercel)
```

---

## Repo layout

| Folder | Purpose | Stack | Hosted on |
| :--- | :--- | :--- | :--- |
| [`frontend/`](frontend) | Web app | Next.js (App Router) + TypeScript | Vercel |
| [`backend/`](backend) | REST API | Express + TypeScript | Railway |
| [`data_pipeline/`](data_pipeline) | ETL: ESPN API → Supabase | Python (`requests`, `pandas`, `supabase`) | Run on demand |
| [`database/`](database) | SQL migrations (schema, functions, triggers, indexes) | PostgreSQL | Supabase |

---

## Database

Postgres on Supabase. Schema designed from an EER model. Core tables:

| Table | Description |
| :--- | :--- |
| `teams` | NFL team information |
| `players` | Player roster data |
| `games` | NFL games by season and week |
| `seasons` | NFL seasons |
| `season_player_stats` | Player performance statistics |
| `season_team_stats` | Aggregated team statistics |
| `game_team_stats` | Team statistics for a single game |
| `player_team_stats` | Player stats in a single game |

Migrations live under [`database/migrations/`](database/migrations).

---

## Running locally

### 1. Backend (Express on Railway)

```bash
cd backend
npm install
cp .env.example .env   # set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
npm run dev            # http://localhost:8080
```

### 2. Frontend (Next.js on Vercel)

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
npm run dev                  # http://localhost:3000
```

### 3. Data pipeline (ETL)

```bash
cd data_pipeline
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install requests pandas supabase
python pull_team_season_data.py
```

See [`data_pipeline/`](data_pipeline) for the per-script entry points.

---

## Deployment

- **Frontend** — Vercel auto-detects Next.js. Set project root to `frontend/` and `NEXT_PUBLIC_API_BASE_URL` to the Railway URL.
- **Backend** — Railway uses `backend/railway.json` (Nixpacks). Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `CORS_ORIGIN` (your Vercel URL).
- **Database** — Apply files in `database/migrations/` to Supabase in order.

---

## Author

Enrique Gamboa — Backend Development | Data Engineering | Database Design
