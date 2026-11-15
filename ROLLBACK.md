# PatientPlex AI — Rollback Plan

## Quick Rollback

### Vercel Frontend
```bash
# List recent deployments
vercel ls

# Roll back to previous deployment
vercel rollback
```
Or: Vercel Dashboard → Deployments → click "..." on previous deploy → "Promote to Production"

### Render Backend
Render Dashboard → PatientPlex AI → Manual Deploy → select previous commit

Or via GitHub:
```bash
git revert HEAD
git push origin main
# Render auto-deploys the revert
```

## Database Rollback

### Alembic Downgrade
```bash
cd backend
# Roll back one migration
alembic downgrade -1

# Roll back to specific revision
alembic downgrade 003  # Roll back to before integration columns
```

### Full Database Reset (DESTRUCTIVE)
```bash
# Only if absolutely necessary — drops all data
cd backend
alembic downgrade base
alembic upgrade head
```

### PostgreSQL Backup/Restore
```bash
# Backup (before deploying)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
```

## Git Operations

### Revert Last Commit
```bash
git revert HEAD --no-edit
git push origin main
```

### Revert Multiple Commits
```bash
# Find the last good commit
git log --oneline -10

# Revert to it (creates new commits)
git revert HEAD~3..HEAD --no-edit
git push origin main
```

### Emergency: Force Reset (DESTRUCTIVE)
```bash
# Only if revert doesn't work — loses commits
git reset --hard <good-commit-sha>
git push --force origin main
```

## Environment Variables

If a deployment breaks due to env var changes:
1. Go to Render Dashboard → Environment
2. Revert the changed variables
3. Click "Save, rebuild, and deploy"

## Known Safe States

| Date | Commit | Description |
|------|--------|-------------|
| 2026-11-15 | `526780e` | Last deployed before CTO audit |
| 2026-11-15 | Current | Post-audit fixes (security, auth, DB) |
