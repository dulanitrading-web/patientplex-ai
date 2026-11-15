# PatientPlex AI — Production Deployment Guide

## Architecture

```
[Browser] → [Vercel CDN] → [Next.js 14 SSR]
                                    ↓
                            [Render Web Service]
                                    ↓
                            [FastAPI + Uvicorn]
                                    ↓
                           [PostgreSQL (Render)]
```

## Current Infrastructure

| Component | Provider | Plan | URL |
|-----------|----------|------|-----|
| Frontend | Vercel | Free | https://patientplex-ai.vercel.app |
| Backend | Render | Free | https://patientplex-ai-g7ce.onrender.com |
| Database | Render | Free | Internal connection string |
| Redis | None | — | Not provisioned |

## Deployment Steps

### Backend (Render)

1. **Source:** GitHub `dulanitrading-web/patientplex-ai`, branch `main`
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Root Directory:** `backend`
5. **Python Version:** Auto-detected (3.11+)

**On every push to main:**
- Render auto-deploys
- Database tables created on startup via `create_all()` + safety ALTER TABLE
- Alembic migrations should be run manually: `alembic upgrade head`

### Frontend (Vercel)

1. **Source:** Same GitHub repo
2. **Framework:** Next.js 14 (auto-detected)
3. **Root Directory:** `frontend`
4. **Build Command:** `npm run build`
5. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://patientplex-ai-g7ce.onrender.com/api/v1
   ```

**On every push to main:**
- Vercel auto-builds and deploys
- Preview deployments for PRs

### Database Migrations

```bash
# From backend directory
cd backend
alembic upgrade head
```

Migrations:
- `001` — Initial schema (doctors, campaigns, conversations, etc.)
- `002` — Add missing tables (call_logs, conversion_events)
- `003` — Optimization tables
- `004` — Integration columns (Google Ads, Meta, Twilio, Razorpay)

## Render Free Tier Limitations

1. **Spin-down:** Service sleeps after 15 min inactivity, ~50s cold start
2. **Memory:** 512MB
3. **CPU:** Shared
4. **Database:** 1GB storage, limited connections
5. **No Redis:** Must provision separately (Upstash free tier recommended)

### Mitigation

- Health check endpoint at `/` prevents unnecessary cold starts
- DB pool size reduced to 5+5 (from 20+10)
- Agent scheduler may strain resources — consider disabling in free tier

## Pre-Deployment Checklist

- [ ] `SECRET_KEY` is not the default value
- [ ] `ENVIRONMENT` set to `production`
- [ ] `ENCRYPTION_KEY` is set (for OAuth token encryption)
- [ ] `BACKEND_BASE_URL` and `FRONTEND_BASE_URL` set correctly
- [ ] All OAuth redirect URIs match actual deploy URLs
- [ ] Google Cloud OAuth consent screen is in Production mode
- [ ] Database migrations are current (`alembic upgrade head`)
- [ ] CORS origins include all production domains

## Monitoring

- **Health check:** `GET /` returns `{"status": "healthy", "agents_scheduled": N}`
- **Backend logs:** Render dashboard → Logs
- **Frontend errors:** Browser console + Vercel logs
- **Database:** Render dashboard → PostgreSQL → Metrics
