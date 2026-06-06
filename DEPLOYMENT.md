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
DATABASE_MODE=postgres
DATABASE_URL=<your Supabase Postgres URL>
FRONTEND_ORIGINS=https://your-vercel-app.vercel.app
FRONTEND_URL=https://your-vercel-app.vercel.app
BACKEND_PUBLIC_URL=https://your-vercel-api.vercel.app
```

After deploy, test:

```text
https://your-vercel-api.vercel.app/health
```

Expected response:

```json
{"status":"ok","database":"postgres"}
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

- Local development defaults to SQLite, even if `DATABASE_URL` exists in the shell.
- `DATABASE_MODE=postgres` must be explicitly set before the backend can use Supabase.
- Production uses Supabase Postgres because serverless function filesystems are not durable application storage.
- The frontend shows an honest retry screen when the backend or OpenDota is unavailable. Production must point `BACKEND_URL` to the Vercel backend project.
- `FRONTEND_URL` and `BACKEND_PUBLIC_URL` are required for the Steam OpenID callback.
- Keep the frontend and backend as separate Vercel projects with `frontend` and `backend` as their respective root directories.

## Automatic Production Deployments

The GitHub Actions workflow at `.github/workflows/deploy-production.yml`
deploys both Vercel projects whenever a commit is pushed to `main`.

One repository secret is required:

```text
VERCEL_TOKEN=<a Vercel access token>
```

Create the token in Vercel account settings, then add it in GitHub under:

```text
Repository Settings > Secrets and variables > Actions > New repository secret
```

The workflow uses the existing Vercel project IDs. Database and application
environment variables remain configured in Vercel and are not copied into
GitHub Actions.

## Local Database Modes

Normal local development uses SQLite:

```text
./scripts/run-backend-local.sh
```

An intentional Supabase integration test uses the ignored `.env.supabase.local` file:

```text
./scripts/run-backend-supabase.sh
```

Check `http://localhost:8000/health`. The `database` value will be either `sqlite` or `postgres`.
