# PatientPlex AI — Final Engineering Audit

**Date:** 2026-11-15
**Auditor:** CTO-level automated review
**Scope:** Full-stack audit of `dulanitrading-web/patientplex-ai`
**Stack:** Next.js 14 (Vercel) + FastAPI (Render) + PostgreSQL + Google Ads REST API

---

## Executive Summary

PatientPlex AI is a healthcare patient acquisition SaaS platform. After a thorough review of 118 backend Python files and 28+ frontend TypeScript files, the platform has **significant production-readiness gaps** that must be addressed before serving real clinic clients.

**Verdict: NOT production-ready.** The platform works for demo flows but has critical security, reliability, and completeness issues.

### Blocking Issues (must fix before any client goes live)

1. **OAuth tokens stored in plaintext** — Google Ads refresh tokens and Meta access tokens are unencrypted in the database
2. **No password reset** — Users who forget passwords are permanently locked out; the frontend fakes the flow
3. **No payment integration** — Razorpay backend exists but frontend never calls it; no way to collect money
4. **OAuth CSRF vulnerability** — Predictable state parameters enable account hijacking
5. **Google Cloud in "Testing" mode** — Only 1 test user can complete OAuth; blocks all other clinics
6. **No token refresh** — JWT expires in 24 hours with no refresh mechanism; users silently lose access
7. **google-ads SDK removed** — Only REST API path works; requires per-doctor OAuth (no global client)

### Key Metrics

| Category | Count |
|----------|-------|
| Total files audited | 146+ |
| Critical issues | 9 |
| High issues | 14 |
| Medium issues | 16 |
| Low issues | 11 |

---

## CRITICAL Issues

### 1. OAuth tokens stored unencrypted in database
**Severity:** CRITICAL | **Component:** Backend
**Files:** `integrations.py:107,242`, `models/doctor.py:80-84`

Google Ads `refresh_token` and Meta Ads `access_token` are stored as plain `Text` in the `doctors` table. `core/encryption.py` with Fernet encryption exists but is never used by the integration endpoints.

**Fix:** Encrypt all OAuth tokens using the existing Fernet encryption before storing. Decrypt on read. Add a migration to encrypt existing tokens.

### 2. Password reset flow is completely fake
**Severity:** CRITICAL | **Component:** Full-stack
**Files:** `api.ts:337-341` (frontend), no backend endpoint exists

The frontend's `requestPasswordReset()` always returns success without calling any backend endpoint. No `/forgot-password` or `/reset-password` endpoints exist. Users see "Check your email" but no email is sent.

**Fix:** Implement backend password reset with email verification tokens. Requires an email service (SendGrid, AWS SES, etc.).

### 3. Razorpay payment has no frontend integration
**Severity:** CRITICAL | **Component:** Frontend
**Files:** `api.ts:316-334`, `billing/page.tsx`

Backend has `createRazorpayOrder` and `verifyRazorpayPayment` endpoints. Frontend defines API functions but **never calls them**. Billing page only has "Start Free Trial". No checkout UI, no Razorpay SDK loaded.

**Fix:** Add Razorpay checkout flow to billing page. Load Razorpay SDK, call `createRazorpayOrder`, open checkout modal, verify payment.

### 4. OAuth state parameter has no CSRF protection
**Severity:** CRITICAL | **Component:** Backend
**Files:** `integrations.py:55-71,151-172`

OAuth state is `"google_ads:{doctor_id}"` — entirely predictable. No random nonce, no HMAC signature. An attacker who knows a doctor's UUID can craft a malicious callback to link their own Google Ads account to the victim's profile.

**Fix:** Generate a random nonce, store it in session/Redis with the doctor_id, and verify it on callback. Use `secrets.token_urlsafe(32)`.

### 5. Google Cloud OAuth in "Testing" mode
**Severity:** CRITICAL | **Component:** Infrastructure
**Location:** Google Cloud Console, project `bdc-agent-507019`

OAuth consent screen is in "Testing" mode with only 1 test user (`anujbhardwaj84@gmail.com`). Any other user attempting OAuth gets a 403 error from Google.

**Fix:** Submit OAuth consent screen for verification and publish to "Production". Requires privacy policy URL and domain verification.

### 6. No JWT token refresh mechanism
**Severity:** CRITICAL | **Component:** Full-stack
**Files:** `auth.tsx`, `api.ts`, `security.py`

JWT expires in 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`). No refresh token is issued. When expired:
- API calls silently fail with 401
- Dashboard pages show empty data (no error message)
- User must manually re-login

**Fix:** Implement refresh token rotation. Issue both access (short-lived, 15-30 min) and refresh (long-lived, 7 days) tokens. Add a `/auth/refresh` endpoint. Add a 401 interceptor in the frontend API client.

### 7. google-ads SDK not installable — REST path only
**Severity:** CRITICAL | **Component:** Backend
**Files:** `requirements.txt`, `google_ads_engine.py`

The `google-ads` Python package was removed because it couldn't install on Render's Python version. The SDK import always fails, `is_connected` is always `False`, and the SDK code path is dead code. Only the REST API path via `connect_with_refresh_token()` works.

**Impact:** Only clinics that complete per-doctor OAuth can use Google Ads features. No global/MCC client path works.

**Fix:** Keep REST API approach (it's actually better — no SDK dependency). Remove dead SDK code. Ensure REST path handles all use cases.

### 8. Login page bypasses AuthProvider
**Severity:** CRITICAL (architectural) | **Component:** Frontend
**Files:** `login/page.tsx:33-36`, `auth.tsx:51-62`

Login page manually stores `pp_token` in localStorage AND a cookie, duplicating `AuthProvider.login()`. The signup page has the same issue. AuthProvider's `login()` is defined but never called.

**Fix:** Consolidate auth logic. Login/signup pages should call `AuthProvider.login()` instead of doing manual token storage.

### 9. Database schema evolution via runtime ALTER TABLE
**Severity:** CRITICAL | **Component:** Backend
**File:** `main.py:66-83`

On every startup, the app runs `ALTER TABLE ADD COLUMN IF NOT EXISTS` for 8 columns. This bypasses Alembic migrations and has no rollback path. Column additions are not version-tracked.

**Fix:** Create proper Alembic migrations for all schema changes. Remove runtime ALTER TABLE from startup.

---

## HIGH Issues

### 10. Three frontend pages bypass the API client
**Files:** `google-business/page.tsx`, `ga4/page.tsx`, `seo/page.tsx`

Use direct `fetch()` instead of `lib/api.ts` helper. Construct API URL differently — if `NEXT_PUBLIC_API_URL` includes `/api/v1`, these pages get a double prefix.

### 11. BACKEND_BASE and FRONTEND_BASE hardcoded
**File:** `integrations.py:25-26`

OAuth callback URLs are hardcoded to Render and Vercel URLs. Must come from environment variables.

### 12. No 401 interceptor in frontend API client
**File:** `api.ts:36-43`

Expired tokens result in empty page states instead of redirect to login.

### 13. Rate limiter broken behind reverse proxy
**File:** `main.py:27`

`get_remote_address` returns proxy IP on Render. Should use `X-Forwarded-For` header.

### 14. Database pool size too large for Render free tier
**File:** `session.py:12`

`pool_size=20, max_overflow=10` = 30 connections. Render free PostgreSQL has limited connections.

### 15. Google Calendar token stored unencrypted
**File:** `models/doctor.py:71`

JSON column with full OAuth token including refresh_token.

### 16. Campaign launch fires on all platforms regardless of connection
**File:** `campaigns/page.tsx:74`

Launches campaigns on Google, Meta, ChatGPT, LinkedIn, WhatsApp without checking connection status.

### 17. Google Ads Disconnect doesn't visually work
**File:** `settings/page.tsx:202-207`

Disconnect clears per-doctor OAuth but status still shows "Connected" if global developer token is set.

### 18. No email verification on signup
No verification that the email belongs to the person signing up.

### 19. Agent scheduler runs all 14 AI agents on startup
**File:** `main.py:89-101`

All AI agents (SEO writer, lead hunter, content creator, etc.) start on various cron schedules. On Render free tier with cold starts, they consume resources and Claude API credits.

### 20. WhatsApp verify has no useful error handling
**File:** `settings/page.tsx:179-184`

Generic `catch { alert("failed") }` with no error detail.

### 21. Cookie max-age mismatch with JWT expiry
**File:** `auth.tsx:56`

Cookie lives 7 days but JWT expires in 24 hours.

### 22. CORS allows Lovable app domain in production
**File:** `main.py:136`

Development URL in production CORS allow list.

### 23. Razorpay verify endpoint lacks Pydantic validation
**File:** `integrations.py:398-475`

Uses `request.json()` directly. Missing fields cause 500 instead of 422.

---

## MEDIUM Issues

24. No error state UI on most dashboard pages
25. SEO page sends empty URL in audit POST
26. Dashboard shows zeros with no guidance for new users
27. Default SECRET_KEY allowed in development mode
28. Redis not available on Render — cache silently fails
29. Billing model is INR-only
30. Missing Alembic migration for doctor integration columns
31. Minimal test coverage (6 test files)
32. WhatsApp API token parsing is fragile
33. Two Google OAuth client secrets enabled
34. Profile editing disabled
35. Account deletion disabled
36. FunnelRow percentage calculation is misleading
37. No structured logging
38. Landing page has hardcoded mock data
39. Google Calendar connect calls onboarding router from settings

---

## LOW Issues

40. Inconsistent loading spinner components
41. Framer-motion used inconsistently
42. No TypeScript strict mode enforcement
43. Hardcoded `en-IN` locale
44. No accessibility attributes
45. DashboardLayout doesn't check onboarding completion
46. Inconsistent import styles in backend
47. EHR router commented out
48. LinkedIn Ads router not registered
49. No health check for database connectivity
50. Alert() used for integration results instead of proper UI

---

## Integration Status Matrix

| Integration | Backend | Frontend | OAuth | API Working | Production Ready |
|------------|---------|----------|-------|-------------|-----------------|
| Google Ads | ✅ REST API | ✅ Connect/Import | ✅ Per-doctor | ⚠️ Untested live | ❌ Testing mode |
| Meta Ads | ✅ Token exchange | ✅ Connect | ✅ Per-doctor | ⚠️ Untested | ❌ Testing mode |
| Google Calendar | ✅ Full | ✅ Connect | ✅ Via onboarding | ✅ Connected for BDC | ⚠️ Redirect URI fixed |
| WhatsApp Cloud | ⚠️ Partial | ✅ Verify | N/A | ⚠️ Token format | ❌ Needs Cloud API setup |
| Twilio Voice | ✅ Full | ✅ Provision | N/A | ⚠️ Trial account | ❌ Needs paid Twilio |
| Razorpay | ✅ Order+Verify | ❌ No checkout UI | N/A | ❌ Not callable | ❌ No frontend |
| LinkedIn Ads | ⚠️ Engine exists | ✅ Status shown | ❌ None | ❌ Token-only | ❌ Not real |
| ChatGPT Ads | ⚠️ Engine exists | ✅ Status shown | ❌ None | ❌ No real API | ❌ Not real |
| Google Business | ⚠️ Demo mode | ✅ Page exists | ❌ None | ❌ Demo data | ❌ Not real |
| GA4 | ⚠️ Demo mode | ✅ Page exists | ❌ None | ❌ Demo data | ❌ Not real |
| SEO | ⚠️ Service exists | ✅ Page exists | N/A | ❌ Empty URL bug | ❌ Not real |

---

## Recommended Fix Priority

### Phase 1: Security (Days 1-3)
1. Encrypt all OAuth tokens with Fernet
2. Add CSRF nonce to OAuth state parameters
3. Move hardcoded URLs to environment variables
4. Fix CORS — remove Lovable domain
5. Fix rate limiter for proxy
6. Reduce DB pool size

### Phase 2: Auth & Accounts (Days 3-5)
1. Implement password reset with email
2. Add email verification on signup
3. Add JWT refresh token rotation
4. Add 401 interceptor in frontend
5. Consolidate login/signup to use AuthProvider
6. Fix cookie max-age to match JWT expiry

### Phase 3: Google Ads Production (Days 5-7)
1. Submit Google Cloud OAuth for production verification
2. Clean up dead SDK code — keep REST-only path
3. Test Import Campaigns end-to-end with BDC account
4. Fix disconnect visual bug
5. Check platform status before campaign launch

### Phase 4: Payment & Billing (Days 7-9)
1. Add Razorpay checkout to billing page
2. Load Razorpay SDK
3. Wire create-order → checkout → verify flow
4. Test with Razorpay test mode

### Phase 5: Database & Infrastructure (Days 9-11)
1. Create Alembic migrations for all missing columns
2. Remove runtime ALTER TABLE from startup
3. Handle Redis absence gracefully
4. Add database health check
5. Disable/configure AI agent scheduler

### Phase 6: Frontend Polish (Days 11-14)
1. Add error states to all dashboard pages
2. Replace alert() with proper toast notifications
3. Fix 3 pages that bypass API client
4. Add new-user guidance on dashboard
5. Fix SEO empty URL bug

---

## Files Changed in This Session

| File | Changes |
|------|---------|
| `backend/app/api/v1/integrations.py` | Error messages, placeholder detection, REST API import flow |
| `backend/app/api/v1/auth.py` | Google Ads "ready" status instead of "connected" |
| `backend/app/services/google_ads_engine.py` | REST API path, connect_with_refresh_token, GAQL fixes |
| `backend/requirements.txt` | Removed google-ads SDK |
| `frontend/src/app/dashboard/settings/page.tsx` | Error handling, Import button for "ready" status |

---

## Environment Variables Status (Render)

| Variable | Set | Notes |
|----------|-----|-------|
| DATABASE_URL | ✅ | PostgreSQL on Render |
| SECRET_KEY | ✅ | Custom value |
| GOOGLE_CLIENT_ID | ✅ | OAuth client for BDC project |
| GOOGLE_CLIENT_SECRET | ✅ | Active |
| GOOGLE_REDIRECT_URI | ✅ | Fixed to -g7ce URL |
| GOOGLE_ADS_DEVELOPER_TOKEN | ✅ | MCC token |
| GOOGLE_ADS_LOGIN_CUSTOMER_ID | ✅ | MCC customer ID |
| META_APP_ID | ✅ | Facebook app |
| META_APP_SECRET | ✅ | Active |
| TWILIO_ACCOUNT_SID | ✅ | Trial account |
| TWILIO_AUTH_TOKEN | ✅ | Trial account |
| RAZORPAY_KEY_ID | ❓ | Not verified |
| RAZORPAY_KEY_SECRET | ❓ | Not verified |
| CLAUDE_API_KEY | ✅ | For AI agents |
| ENCRYPTION_KEY | ✅ | Fernet key (but not used for OAuth tokens) |
| REDIS_URL | ❌ | Not set — no Redis on Render free tier |
