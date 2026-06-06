# DotaReframe Deployment

Recommended free MVP setup:

```text
Frontend: Vercel Project
Backend: Vercel Project
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

The backend creates the `reports` table automatically when needed.

## 2. Vercel Backend

Create a Vercel project from this GitHub repo.

Use these settings:

```text
Framework Preset: Other
Root Directory: backend
```

Environment variables:

```text
DATABASE_URL=<your Supabase Postgres URL>
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
```

After deploy, test:

```text
https://your-vercel-api.vercel.app/health
```

Expected response:

```json
{"status":"ok"}
```

## 3. Vercel Frontend

Create a second Vercel project from the same GitHub repo.

Use these settings:

```text
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
```

Environment variable:

```text
BACKEND_URL=https://your-vercel-api.vercel.app
```

After the frontend deploys, set its production URL as the backend project's `FRONTEND_ORIGINS`, then redeploy the backend.

## Notes

- Local development still uses SQLite when `DATABASE_URL` is not set.
- Production uses Supabase Postgres because serverless function filesystems are not durable application storage.
- The frontend has sample fallback data if the backend is unreachable, but production should point `BACKEND_URL` to the Vercel backend project.
- Keep the frontend and backend as separate Vercel projects with `frontend` and `backend` as their respective root directories.
