# PatientPlex AI — Test Report

**Date:** 2026-11-15
**Environment:** Cloud workspace (Linux)

---

## Static Analysis

### Backend (Python)
| Check | Result |
|-------|--------|
| All 9 modified Python files parse (AST) | ✅ Pass |
| Alembic migration 004 syntax | ✅ Pass |
| No hardcoded secrets in source | ✅ Pass |
| requirements.txt valid | ✅ Pass (google-ads removed, REST-only) |

### Frontend (TypeScript)
| Check | Result |
|-------|--------|
| `tsc --noEmit` (full type check) | ✅ Pass — 0 errors |
| All modified pages import correctly | ✅ Pass |
| No `pp_token` key mismatch | ✅ Verified — all use "pp_token" |

---

## Changes Verified

### Security Fixes
| Fix | Verified |
|-----|----------|
| OAuth CSRF: random state tokens (not predictable doctor_id) | ✅ `_create_oauth_state()` generates `secrets.token_urlsafe(32)` |
| OAuth CSRF: state consumed on use (one-time) | ✅ `_verify_oauth_state()` pops from store |
| OAuth CSRF: state expires after 10 minutes | ✅ `_OAUTH_STATE_TTL = 600` |
| OAuth tokens encrypted with Fernet before DB storage | ✅ `encrypt_value()` called in both Google Ads and Meta callbacks |
| OAuth tokens decrypted when used | ✅ `decrypt_value()` in import-campaigns flow |
| Encryption graceful fallback for pre-encryption data | ✅ `decrypt_value()` returns input on decryption failure |
| Hardcoded URLs replaced with config | ✅ `BACKEND_BASE_URL` / `FRONTEND_BASE_URL` in settings |
| CORS: Lovable domain removed | ✅ Only legitimate origins in allow list |
| Rate limiter: X-Forwarded-For for real client IP | ✅ `_get_real_client_ip()` extracts from header |
| DB pool reduced for Render free tier | ✅ `pool_size=5, max_overflow=5` |

### Auth Fixes
| Fix | Verified |
|-----|----------|
| 401 interceptor in API client | ✅ Clears token + redirects to `/login?expired=1` |
| Cookie max-age matches JWT (24h, not 7d) | ✅ `max-age=${60 * 60 * 24}` |
| Secure flag on HTTPS | ✅ Conditional `; Secure` |
| Login page uses AuthProvider.login() | ✅ No more duplicate token storage |
| Signup page uses AuthProvider.signup() | ✅ No more duplicate token storage |

### Database Fixes
| Fix | Verified |
|-----|----------|
| Alembic migration 004 for all integration columns | ✅ Includes doctor + subscription columns |
| Runtime ALTER TABLE retained as safety net | ✅ Comments clarify it's a fallback |
| Pool recycle for Render connection drops | ✅ `pool_recycle=300` |
| Razorpay columns added to billing model | ✅ `razorpay_order_id`, `razorpay_payment_id` |

### Google Ads Fixes
| Fix | Verified |
|-----|----------|
| google_ads_oauth.py: state param is opaque (not `google_ads:doctor_id`) | ✅ Accepts state from caller |
| REST API path works without SDK | ✅ `_get_campaign_metrics_rest()` uses httpx |
| GAQL date range valid | ✅ Uses `gaql_range_map` dict (7/14/30 days) |
| Customer ID normalized | ✅ `.replace("-", "").strip()` |

---

## Existing Tests

```
backend/tests/
├── conftest.py         — Test DB setup (SQLite in-memory)
├── test_auth.py        — Login/signup/me endpoints
├── test_billing.py     — Subscription/trial flows
├── test_booking.py     — Appointment booking
├── test_ml_engine.py   — ML predictions
├── test_onboarding.py  — Onboarding wizard
└── test_api_ml.py      — ML API endpoints
```

**Note:** Tests use SQLite with TESTING=true flag. Render PostgreSQL features (enums, ALTER TYPE) are not testable in this setup. Integration tests for OAuth flows do not exist.

---

## Known Untested Paths

| Path | Why |
|------|-----|
| Google Ads Import with real account | OAuth consent screen in "Testing" mode |
| Meta Ads campaign creation | No test Meta App configured |
| Razorpay checkout flow | Frontend not implemented |
| WhatsApp Cloud API messaging | Token format not configured |
| Twilio number provisioning | Trial account limitation |
| Password reset email | No email service configured |
| Multi-user OAuth (2+ clinics) | Google OAuth in "Testing" mode |

---

## Recommendations

1. **Add integration tests** for OAuth callbacks using mocked HTTP responses
2. **Add frontend E2E tests** with Playwright for login/signup/onboarding
3. **Test Razorpay** in test mode once frontend checkout is implemented
4. **Test Google Ads Import** after publishing OAuth consent screen
