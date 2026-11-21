# Security — Environment Variables & Secrets

**DO NOT commit secret values to this file or any file in the repository.**

This document lists all environment variables, their sensitivity level, and rotation procedures.

## Sensitive Variables (rotate immediately if leaked)

| Variable | Service | Rotation |
|----------|---------|----------|
| `SECRET_KEY` | JWT signing | Generate new: `python -c "import secrets; print(secrets.token_hex(32))"` → update on Render → all sessions invalidated |
| `ENCRYPTION_KEY` | Field-level encryption (OAuth tokens at rest) | Generate new: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` → re-encrypt stored tokens |
| `DATABASE_URL` | PostgreSQL connection | Rotate in Render PostgreSQL dashboard → update env var |
| `CLAUDE_API_KEY` | Anthropic API | Rotate at https://console.anthropic.com/ |
| `FREE_LLM_API_KEY` | Groq API | Rotate at https://console.groq.com/ |
| `EXOTEL_API_KEY` | Exotel telephony | Rotate at https://my.exotel.com → API Settings |
| `EXOTEL_API_TOKEN` | Exotel telephony | Same as above |
| `TWILIO_AUTH_TOKEN` | Twilio (backup) | Rotate at https://console.twilio.com |
| `WHATSAPP_API_TOKEN` | Meta Cloud API | Regenerate at https://developers.facebook.com → WhatsApp → API Setup |
| `WHATSAPP_VERIFY_TOKEN` | Meta webhook verification | Change on both Render AND Meta developer console simultaneously |
| `META_APP_SECRET` | Meta webhook signature verification | Rotate at https://developers.facebook.com → App Settings → Basic |
| `RAZORPAY_KEY_SECRET` | Razorpay payments | Rotate at https://dashboard.razorpay.com |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay webhook verification | Rotate in Razorpay webhook settings |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | Rotate at https://console.cloud.google.com/apis/credentials |
| `SMTP_PASSWORD` | Email sending | Rotate with email provider |
| `RESEND_API_KEY` | Resend email API | Rotate at https://resend.com |

## Non-Sensitive Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENVIRONMENT` | development/staging/production | development |
| `CALL_PROVIDER` | "exotel" or "twilio" | exotel |
| `EXOTEL_SID` | Exotel account ID | — |
| `EXOTEL_CALLER_ID` | ExoPhone virtual number | — |
| `TWILIO_ACCOUNT_SID` | Twilio account ID | — |
| `TWILIO_PHONE_NUMBER` | Twilio virtual number | — |
| `WHATSAPP_API_URL` | Meta Graph API base URL | https://graph.facebook.com/v25.0 |
| `WHATSAPP_PHONE_NUMBER_ID` | Meta phone number ID | — |
| `META_APP_ID` | Meta app ID | — |
| `RAZORPAY_KEY_ID` | Razorpay public key | — |
| `CLINIC_DEFAULT_OPEN_TIME` | Default clinic opening | 09:00 |
| `CLINIC_DEFAULT_CLOSE_TIME` | Default clinic closing | 20:00 |
| `SLOT_DURATION_MINUTES` | Appointment slot length | 30 |
| `MISSED_CALL_WHATSAPP_DELAY_SECONDS` | Delay before missed call follow-up | 30 |
| `FREE_LLM_BASE_URL` | OpenAI-compatible endpoint | — |
| `FREE_LLM_MODEL` | Model name | llama-3.3-70b-versatile |
| `EMAIL_PROVIDER` | "smtp" or "resend" | smtp |
| `EMAIL_FROM_NAME` | Sender display name | PatientPlex AI |
| `ADS_ENABLED` | Enable ad platform integrations | false |

## Where Secrets Are Stored

- **Production:** Render Dashboard → Environment Variables (https://dashboard.render.com/web/srv-dbsb2pk9v7es73c795jg/env)
- **Local development:** `backend/.env` (gitignored, never commit)
- **Template:** `backend/.env.example` (no values, safe to commit)

## Security Checklist

- [ ] `SECRET_KEY` is not the default value in production
- [ ] `ENCRYPTION_KEY` is set in production
- [ ] `META_APP_SECRET` is set for webhook signature verification
- [ ] No secrets in git history
- [ ] `.env` is in `.gitignore`
- [ ] Exotel webhook IP whitelist configured (when available)
- [ ] CORS origins restricted in production
- [ ] Rate limiting enabled on auth and webhook endpoints

## Known Security Gaps (to fix)

1. **CORS:** Currently allows all origins — restrict to `patientplex-ai.vercel.app` in production
2. **Exotel webhook verification:** Currently checks `CALL_PROVIDER` only — add IP whitelist when Exotel publishes their range
3. **Session tokens:** No refresh token rotation — access tokens last 24h with no revocation
4. **Multi-tenancy:** Single-clinic fallback exists in call routing — remove for multi-clinic
