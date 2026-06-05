# DotaReframe Deployment

Recommended free MVP setup:

```text
Frontend: Vercel
Backend: Render Web Service
Database: Supabase Postgres
```

## 1. Supabase Postgres

1. Create a Supabase project.
2. Copy the Postgres connection string.
3. Use the pooled or direct connection string as `DATABASE_URL`.
4. Make sure the connection string includes SSL, for example:

```text
postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require
```

The backend creates the `reports` table automatically on startup.

## 2. Render Backend

Create a Render Web Service from this GitHub repo.

Use these settings:

```text
Root Directory: .
Runtime: Python
Build Command: pip install -r backend/requirements.txt
Start Command: PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```text
DATABASE_URL=<your Supabase Postgres URL>
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
```

After deploy, test:

```text
https://your-render-service.onrender.com/health
```

Expected response:

```json
{"status":"ok"}
```

## 3. Vercel Frontend

Create a Vercel project from this GitHub repo.

Use these settings:

```text
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
```

Environment variable:

```text
BACKEND_URL=https://your-render-service.onrender.com
```

After Vercel gives you a production URL, copy it into Render's `FRONTEND_ORIGINS` and redeploy the backend.

## Notes

- Local development still uses SQLite when `DATABASE_URL` is not set.
- Production should use Supabase Postgres because Render free web services have an ephemeral filesystem.
- Render free services sleep after idle time, so the first request can be slow.
- The frontend has sample fallback data if the backend is unreachable, but production should point `BACKEND_URL` to Render.
