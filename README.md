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
- **Backend** — Railway uses `backend/railway.json` (Nixpacks auto-detects the Maven project and runs `java -jar target/app.jar`). Set `CORS_ORIGIN` (your Vercel URL), and — once DB access is enabled — `SUPABASE_DB_URL`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`.
- **Database** — Apply files in `database/migrations/` to Supabase in order.

---

## Author

Enrique Gamboa — Backend Development | Data Engineering | Database Design
