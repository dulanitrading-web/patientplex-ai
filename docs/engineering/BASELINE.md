# PatientPlex AI — Engineering Baseline

**Date:** 2026-11-08
**Starting commit:** c609baf (Phase 1 fixes applied)

## Current State

### What Works
- Auth (signup/login/JWT) — token key fixed to pp_token
- 4-step onboarding wizard — API-connected
- AI WhatsApp receptionist — Claude tool-use loop (calendar db param fixed)
- WhatsApp messaging — Meta Cloud API
- Booking engine — calendar db param fixed
- Missed call detection — Twilio TwiML
- Conversion tracker — metadata field fixed
- Landing page generator — self-contained HTML
- Appointment CRUD — status updates, stats
- Ad copy generator — Claude API with template fallback
- Billing plan gating — Razorpay credentials fixed

### Critical Issues Remaining
1. No Alembic migration for call_logs, conversion_events, subscriptions, invoices
2. Default SECRET_KEY still accepted (warning added but not blocked)
3. All webhooks accept unverified requests
4. No rate limiting
5. OAuth tokens stored as plaintext JSON
6. Multi-tenant WhatsApp routing falls back to first doctor
7. Double header on dashboard page
8. 5 sidebar nav links to nonexistent pages
9. Two incompatible design systems (dark landing vs light dashboard)
10. Zero frontend tests, 20 backend tests with wrong assertions

### Files: 141 total
### Backend: 16 services, 11 route files, 5 models, 48 endpoints
### Frontend: 9 pages, 16 UI components (11 unused)
### Tests: 4 backend test files, 0 frontend tests
