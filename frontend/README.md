# frontend

NFL Stats web app. Next.js (App Router) + TypeScript, deployed on [Vercel](https://vercel.com/).

## Local development

```bash
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_BASE_URL to your backend
npm run dev
```

App runs on `http://localhost:3000`.

## Scripts

- `npm run dev` — Next dev server
- `npm run build` — production build
- `npm start` — serve production build
- `npm run typecheck` — type-check only

## Deploying to Vercel

1. Import this repo in Vercel and set the project root to `frontend/`.
2. Set env var `NEXT_PUBLIC_API_BASE_URL` to the Railway backend URL.
3. Push — Vercel auto-detects Next.js.

## Layout

```
src/
  app/             # App Router pages, layouts, route handlers
  lib/api.ts       # fetch helper pointed at the backend
public/            # static assets
```
