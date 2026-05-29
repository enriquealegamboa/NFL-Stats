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
  server.ts             # Express app + boot
  routes/               # route modules (health, ...)
  lib/
    supabase.ts         # Supabase client
    errors.ts           # error codes + AppError / ValidationError / NotFoundError
  middleware/
    validate.ts         # validate(schema, source?) — Zod-backed request validator
    errorHandler.ts     # central error-to-envelope handler (registered last)
```

## Error format

Every error response uses the same envelope:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": { "issues": [ { "path": "body.message", "message": "Required", "code": "invalid_type" } ] }
  }
}
```

- `code` — stable string constant. Current codes: `VALIDATION_FAILED` (400), `NOT_FOUND` (404), `INTERNAL_ERROR` (500).
- `message` — human-readable summary. Safe to surface to end users.
- `details` — optional, code-specific payload. For `VALIDATION_FAILED`, an `issues[]` array with `path` / `message` / `code` per Zod issue.

Unhandled errors are logged server-side and returned as an opaque `INTERNAL_ERROR` 500 — stack traces are never sent in the response body.

### Smoke test

```bash
# Success
curl -s -X POST http://localhost:8080/health/echo \
  -H 'content-type: application/json' \
  -d '{"message":"hello"}'
# -> {"echoed":"hello"}

# Validation failure
curl -s -X POST http://localhost:8080/health/echo \
  -H 'content-type: application/json' \
  -d '{}'
# -> {"error":{"code":"VALIDATION_FAILED", ...}}
```
