# backend

NFL Stats REST API. Express + TypeScript, deployed on [Railway](https://railway.app/), data from [Supabase](https://supabase.com/).

## Local development

```bash
npm install
cp .env.example .env   # fill in SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
npm run dev
```

Server runs on `http://localhost:8080`. Health check at `/health`.

## Scripts

- `npm run dev` — watch mode (tsx)
- `npm run build` — compile TypeScript to `dist/`
- `npm start` — run compiled output (used by Railway)
- `npm run typecheck` — type-check only

## Deploying to Railway

Railway auto-detects Node and uses `railway.json` for build/start/healthcheck.

1. Create a new Railway project and link this folder (or set the service root to `backend/`).
2. Set env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `CORS_ORIGIN` (your Vercel URL).
3. Push to the connected branch.

## Layout

```
src/
  server.ts        # Express app + boot
  routes/          # route modules (health, ...)
  lib/supabase.ts  # Supabase client
```
