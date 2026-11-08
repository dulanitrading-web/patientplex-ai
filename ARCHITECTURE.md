# PatientPlex AI — Architecture Audit & Implementation Plan

**Audit Date:** 2026-11-08
**Repository:** github.com/dulanitrading-web/patientplex-ai
**Commit:** 608f9b5 (v4.0 — single commit, entire codebase)

---

## Executive Summary

PatientPlex AI is an **MVP-stage healthcare SaaS** with a well-designed architecture that is approximately **60-70% real working code** and 30-40% structured placeholders. The core differentiators (AI WhatsApp receptionist, missed-call recovery, conversion funnel tracking) have genuine implementations. The ad platform integrations (Google Ads, Meta Ads, LinkedIn) are detailed placeholders. There are **3 runtime-crashing bugs**, a **ship-blocking auth bug on the frontend**, and **6 security vulnerabilities** that must be fixed before any deployment.

### Verdict
This is a legitimate product codebase, not a demo. With targeted fixes (not a rewrite), it can reach a functional MVP.

---

## 1. What Works (Real, Tested Code)

| Component | Status | Notes |
|-----------|--------|-------|
| **Auth (signup/login/JWT)** | ✅ Working | Properly implemented bcrypt + JWT |
| **Onboarding (4-step wizard)** | ✅ Working | Best-built feature in the app, API-connected |
| **AI Receptionist (Claude API)** | ✅ Working* | Real tool-use loop with Claude, *calendar bug |
| **WhatsApp messaging (Meta Cloud API)** | ✅ Working | Send/receive via Meta, conversation storage |
| **Booking Engine** | ✅ Working* | Full orchestration, *calendar bug |
| **Call Handler (Twilio TwiML)** | ✅ Working | Incoming calls, missed-call detection |
| **Conversion Tracker (17-stage funnel)** | ✅ Working* | Full attribution, *metadata field bug |
| **Landing Page Generator** | ✅ Working | Self-contained HTML with Schema.org |
| **Appointment Management** | ✅ Working | CRUD, status updates, stats |
| **Ad Copy Generator (Claude API)** | ✅ Working | With template fallback |
| **Reminder Service** | ✅ Working | 24h + 2h WhatsApp reminders |
| **Billing / Plan Gating** | ✅ Partial | Plan enforcement works, Razorpay is placeholder |
| **UI Component Library (16 components)** | ✅ Good | Well-typed, reusable, dark mode partial |
| **Tests (20 test cases)** | ✅ Partial | Auth, onboarding, booking, billing covered |

## 2. What Is Broken (Must Fix Before Deployment)

### CRITICAL — Runtime Crashes

| # | Bug | Location | Impact |
|---|-----|----------|--------|
| 1 | **GoogleCalendarService method signature mismatch** — `get_available_slots(doctor_id, date, db)` requires `db` param, but AIReceptionist and BookingEngine call it without `db` | `backend/app/services/ai_receptionist.py`, `booking_engine.py`, `google_calendar.py` | Crashes when Google Calendar is connected |
| 2 | **ConversionTracker references `e.metadata`** but model field is `e.extra_data` | `backend/app/services/conversion_tracker.py` | Patient journey endpoint crashes |
| 3 | **BillingService uses `SECRET_KEY` as Razorpay credentials** — `self.key_id = settings.SECRET_KEY` | `backend/app/services/billing_service.py` | Razorpay calls would use JWT secret as API key |

### CRITICAL — Ship-Blocking Auth Bug

| # | Bug | Location | Impact |
|---|-----|----------|--------|
| 4 | **Frontend token key mismatch** — Login/signup pages store JWT as `localStorage["token"]`, but auth context, useApi hook, and middleware all read `localStorage["pp_token"]` | `frontend/src/app/login/page.tsx` (line 35), `signup/page.tsx` (line 56), `context/auth.tsx` (line 48), `middleware.ts` (line 9) | **Users cannot log in.** After successful authentication, middleware redirects back to login because it can't find the token. |

### HIGH — Missing Database Tables

| # | Bug | Location | Impact |
|---|-----|----------|--------|
| 5 | **Alembic migration 001 only creates 4 of 8 tables** — Missing: call_logs, conversion_events, subscriptions, invoices | `backend/alembic/versions/001_initial_schema.py`, `alembic/env.py`, `create_tables.py` | Production deployment via Alembic would be missing half the schema |

## 3. Security Vulnerabilities

| Severity | Issue | Location |
|----------|-------|----------|
| 🔴 CRITICAL | Default `SECRET_KEY = "change-this-..."` — anyone can forge JWTs | `backend/app/core/config.py` |
| 🔴 HIGH | CORS `allow_origins=["*"]` with `allow_credentials=True` | `backend/app/main.py` |
| 🔴 HIGH | Google OAuth tokens stored as plain JSON (unencrypted) | `backend/app/models/doctor.py` |
| 🟠 HIGH | No rate limiting on any endpoint | Global |
| 🟠 HIGH | Razorpay webhook signature verification commented out | `backend/app/api/v1/billing.py` |
| 🟡 MEDIUM | WhatsApp webhook verify_token not checked | `backend/app/api/v1/whatsapp.py` |
| 🟡 MEDIUM | Twilio webhook requests not validated | `backend/app/api/v1/calls.py` |
| 🟡 MEDIUM | WhatsApp falls back to "first active doctor" in multi-tenant | `backend/app/api/v1/whatsapp.py` |

## 4. What Is Missing

### Backend — Not Yet Implemented
1. **Google Ads API integration** — placeholder with commented-out code
2. **Meta Ads API integration** — placeholder
3. **LinkedIn Ads API integration** — placeholder
4. **Razorpay payment processing** — placeholder
5. **Exotel voice integration** — config exists, no code
6. **Email service** — no email sending (password reset, invoices)
7. **Patient model** — patients tracked only by phone number
8. **Multi-doctor WhatsApp routing** — single-number routing only
9. **File uploads** — no image storage for clinics/doctors
10. **Google Calendar event deletion on cancel** — TODO in code

### Frontend — Not Yet Built
1. `/dashboard/calls` — in sidebar nav, page doesn't exist
2. `/dashboard/conversions` (Funnel) — in sidebar nav, page doesn't exist
3. `/dashboard/settings` — in sidebar nav, no page
4. Password reset / forgot password flow
5. User profile / account settings
6. Billing / subscription management page
7. Analytics with real charts (no charting library installed)
8. Notification center
9. 404 page
10. Any use of the `useApi.ts` hooks (completely unused)

## 5. Code Quality Issues

### Frontend
- **Duplicate file:** `page_v4.tsx` is byte-for-byte identical to `page.tsx` (995 lines of dead code)
- **Three API implementations:** `lib/api.ts`, `hooks/useApi.ts`, `context/auth.tsx` each have their own fetch logic with different token key names
- **Double header:** Dashboard page renders its own header while DashboardLayout also renders header + sidebar
- **Hardcoded localhost:** Landing page preview URL is `http://localhost:8000`
- **Market inconsistency:** Landing page shows USD + US cities; dashboard/onboarding uses INR + Indian pincodes
- **Accessibility failures:** No ARIA attributes, 8-9px font sizes, contrast failures, no focus management
- **Zero frontend tests**
- **Package name mismatch:** `cliniccare-frontend` in package.json

### Backend
- **Missing model relationships:** No `relationship()` declarations between Doctor → Campaign, Subscription, etc.
- **Reminder query performance:** Loads ALL appointments and filters in Python instead of SQL
- **Hardcoded budget splits:** 50% Google, 40% Meta, 10% LinkedIn — not configurable
- **CallDirection enum:** `MISSED` is listed as a direction (semantic error)
- **No structured logging** — uses print statements
- **Test conftest assertion bug:** `test_signup` asserts status 200 but endpoint returns 201

---

## 6. Recommended Tech Stack (Final)

### Keep (Already Working)
| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend Framework | FastAPI | Well-implemented, async, production-ready |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 async | Solid, already working |
| Migrations | Alembic | Standard, already configured |
| Auth | JWT (python-jose + bcrypt) | Working, just needs security fixes |
| Frontend Framework | Next.js 14 (App Router) | Already in use, good choice |
| Styling | Tailwind CSS | Already in use |
| Icons | Lucide React | Already in use |

### Add
| Layer | Technology | Reason |
|-------|-----------|--------|
| UI Components | shadcn/ui + Radix primitives | Replace custom components with accessible, tested ones |
| Forms | React Hook Form + Zod | Replace manual form state |
| Data Fetching | TanStack Query | Replace manual useEffect/fetch |
| Charts | Recharts | Dashboard visualizations |
| Tables | TanStack Table | Campaign/appointment data tables |
| Animation | Framer Motion (light use) | Polish transitions, avoid excess |
| Background Jobs | Redis + ARQ (or Celery) | Replace APScheduler for distributed tasks |
| Rate Limiting | slowapi | FastAPI-compatible |
| Logging | structlog | Structured JSON logging |
| Error Tracking | Sentry | Frontend + backend |
| Testing (FE) | Vitest + Testing Library | Component + integration tests |
| Testing (E2E) | Playwright | Full flow testing |

### Do NOT Add
| Technology | Reason |
|-----------|--------|
| Zustand/Redux | Auth context + TanStack Query covers all state needs |
| Prisma | SQLAlchemy is already working well |
| tRPC | REST API is fine, already built |
| GraphQL | Unnecessary complexity for this product |
| Kubernetes | Docker Compose is appropriate for this stage |

---

## 7. Implementation Roadmap

### Phase 1 — Critical Fixes (Week 1)
**Objective:** Make the existing code actually runnable.

1. Fix token key mismatch (`"token"` → `"pp_token"` everywhere)
2. Fix GoogleCalendarService method signatures
3. Fix ConversionTracker `metadata` → `extra_data`
4. Fix BillingService Razorpay credentials
5. Fix create_tables.py and Alembic to include all 8 models
6. Generate proper Alembic migration for missing tables
7. Delete `page_v4.tsx` duplicate
8. Remove double header from dashboard
9. Fix hardcoded localhost URL
10. Consolidate API layer (keep `lib/api.ts`, delete `hooks/useApi.ts`)
11. Restrict CORS origins
12. Generate a proper default SECRET_KEY with instructions

### Phase 2 — Design System & Layout (Week 2)
**Objective:** Unified, premium UI foundation.

1. Install shadcn/ui, Radix, React Hook Form, Zod, TanStack Query, Recharts
2. Create design tokens (colors, typography, spacing)
3. Build the app shell (sidebar, topbar, clinic switcher, search)
4. Settle on light default + dark mode toggle (not dark-only)
5. Build common patterns: page header, filter bar, empty state, loading
6. Responsive mobile navigation
7. Write DESIGN_SYSTEM.md

### Phase 3 — Frontend Pages (Weeks 3-4)
**Objective:** Production-quality dashboard connected to real APIs.

1. Dashboard with real KPI cards, charts, funnel visualization
2. Campaign management (list, create, pause/resume, metrics)
3. Patient conversations (inbox, chat viewer, AI takeover)
4. Appointments (calendar view, status management, reminders)
5. Calls (call log, missed call recovery stats)
6. Conversion funnel (visual pipeline, attribution)
7. Settings (profile, clinic, integrations, billing)
8. Analytics & ROI

### Phase 4 — Backend Hardening (Weeks 4-5)
**Objective:** Production-grade backend.

1. Add model relationships
2. Multi-tenancy: tenant-scoped queries on all endpoints
3. Add Patient model
4. Rate limiting (slowapi)
5. Webhook signature verification (Twilio, Meta, Razorpay)
6. Structured logging
7. Redis + background worker for WhatsApp follow-ups and reminders
8. API documentation (auto-generated OpenAPI is already present)

### Phase 5 — AI Engine (Week 6)
**Objective:** Polish the AI receptionist and add the ad assistant.

1. Fix AI receptionist calendar integration
2. Add multi-language support
3. Implement approval workflow for AI actions
4. Build AI ad optimization assistant
5. Add tool-use guardrails and escalation rules

### Phase 6 — Integrations (Weeks 7-8)
**Objective:** Connect real ad platforms and payments.

1. Google Ads API (requires developer token approval — start application now)
2. Meta Marketing API (requires app review)
3. Razorpay Subscriptions API
4. Exotel voice integration
5. Email service (Resend or AWS SES)

### Phase 7 — Security & Testing (Week 9)
**Objective:** Production-ready security and test coverage.

1. Encrypt OAuth tokens at rest
2. HTTPS enforcement
3. Audit logging
4. DPDP Act compliance controls
5. Backend test coverage: webhooks, AI receptionist, campaigns, multi-tenant isolation
6. Frontend tests: auth flow, onboarding, dashboard
7. E2E tests: signup → onboarding → campaign → booking → conversion

### Phase 8 — Production Deployment (Week 10)
**Objective:** Staging + production environments.

1. Staging environment with seed data
2. Production Docker Compose with health checks
3. CI/CD pipeline (GitHub Actions)
4. Database backup automation
5. Monitoring (Sentry + uptime)
6. DEPLOYMENT.md with runbook

---

## 8. Top 20 Improvements (Priority Order)

| # | Improvement | Complexity | Impact |
|---|------------|-----------|--------|
| 1 | Fix auth token mismatch | Low | Ship-blocking |
| 2 | Fix 3 runtime crash bugs | Low | Ship-blocking |
| 3 | Fix missing DB tables in migrations | Low | Ship-blocking |
| 4 | Security: CORS, secrets, webhook verification | Medium | Security-critical |
| 5 | Consolidate frontend API layer | Low | Code quality |
| 6 | Unified design system (light + dark) | Medium | User experience |
| 7 | Real dashboard with charts and live data | Medium | Core product value |
| 8 | Patient CRM model and pages | Medium | Product completeness |
| 9 | Rate limiting | Low | Security |
| 10 | Structured logging | Low | Operability |
| 11 | Redis + proper background workers | Medium | Reliability |
| 12 | Multi-tenant query scoping | Medium | Security-critical at scale |
| 13 | Google Ads API integration | High | Core value proposition |
| 14 | Razorpay payment integration | Medium | Revenue |
| 15 | Frontend testing suite | Medium | Reliability |
| 16 | Mobile-responsive dashboard | Medium | User experience |
| 17 | Appointment calendar view | Medium | User experience |
| 18 | Conversion funnel visualization | Medium | Product differentiation |
| 19 | Email notifications | Medium | Product completeness |
| 20 | E2E test suite (Playwright) | High | Confidence in changes |

---

## 9. File Structure (Current)

```
patientplex-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, CORS, routes
│   │   ├── workers.py                 # APScheduler background jobs
│   │   ├── core/
│   │   │   ├── config.py              # Pydantic Settings
│   │   │   └── security.py            # JWT + bcrypt
│   │   ├── db/
│   │   │   ├── base.py                # SQLAlchemy Base
│   │   │   └── session.py             # Async engine + session
│   │   ├── models/                    # 5 model files, 8 tables
│   │   ├── schemas/                   # Pydantic schemas
│   │   ├── services/                  # 16 service files
│   │   └── api/v1/                    # 11 route files
│   ├── alembic/                       # Migrations (incomplete)
│   ├── tests/                         # 4 test files, 20 cases
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js App Router pages
│   │   │   ├── page.tsx               # Landing page (995 lines, demo data)
│   │   │   ├── page_v4.tsx            # DUPLICATE — delete
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   ├── onboarding/page.tsx
│   │   │   └── dashboard/            # 5 dashboard pages
│   │   ├── components/
│   │   │   ├── ui/                    # 16 reusable components
│   │   │   └── layout/               # DashboardLayout
│   │   ├── hooks/useApi.ts            # UNUSED — delete or adopt
│   │   ├── lib/api.ts                 # Primary API client
│   │   ├── context/auth.tsx           # Auth context provider
│   │   └── styles/globals.css
│   ├── package.json
│   └── Dockerfile
├── nginx/cliniccare.conf
├── docker-compose.yml
├── docker-compose.prod.yml
└── DEPLOY.md
```

---

*This audit is the foundation for all implementation work. Phase 1 (Critical Fixes) should start immediately.*
