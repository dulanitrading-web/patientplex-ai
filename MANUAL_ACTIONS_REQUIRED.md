# PatientPlex AI — Manual Actions Required

These actions require human intervention and cannot be automated through code changes.

---

## 🔴 BLOCKING — Must Complete Before Go-Live

### 1. Publish Google Cloud OAuth Consent Screen
**Who:** Prakash (GCP admin)
**Where:** https://console.cloud.google.com → APIs & Services → OAuth consent screen
**What:**
- Current state: "Testing" — only `anujbhardwaj84@gmail.com` can authorize
- Click "Publish App" to move to Production
- Requires: Privacy policy URL, Terms of service URL, domain verification
- **Without this, no other clinic can connect Google Ads or Calendar**

### 2. Revoke Extra OAuth Client Secret
**Who:** Prakash (GCP admin)
**Where:** https://console.cloud.google.com → Credentials → OAuth 2.0 Client IDs → Web client 1
**What:**
- 2 client secrets are enabled — security risk
- Keep the one that matches `GOOGLE_CLIENT_SECRET` env var on Render
- Delete the other one

### 3. Upgrade Twilio from Trial to Paid
**Who:** Prakash (Twilio admin)
**Where:** https://console.twilio.com
**What:**
- Trial account cannot provision numbers programmatically
- Upgrade to pay-as-you-go ($20 minimum)
- Enable India number capability (requires business verification)

### 4. Set BACKEND_BASE_URL and FRONTEND_BASE_URL on Render
**Who:** Prakash (Render admin)
**Where:** https://dashboard.render.com → PatientPlex AI → Environment
**What:**
```
BACKEND_BASE_URL=https://patientplex-ai-g7ce.onrender.com
FRONTEND_BASE_URL=https://patientplex-ai.vercel.app
```
These are currently using default values in code but should be explicit env vars.

### 5. Set Up Email Service for Password Reset
**Who:** Prakash (developer)
**What:**
- Sign up for SendGrid, AWS SES, or Resend
- Get API key
- Add `EMAIL_API_KEY` and `EMAIL_FROM` to Render env vars
- Backend password reset endpoint needs implementation (code TODO)

### 6. Verify Razorpay Credentials
**Who:** Prakash (Razorpay admin)
**Where:** https://dashboard.razorpay.com
**What:**
- Confirm `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set on Render
- Ensure KYC is complete for live mode
- Test mode works without KYC

---

## 🟡 IMPORTANT — Should Complete Within 2 Weeks

### 7. Set Up WhatsApp Business API
**Who:** Prakash (Meta Business admin)
**Where:** https://business.facebook.com → WhatsApp
**What:**
- Apply for WhatsApp Business API access
- Create and verify a WhatsApp Business phone number
- Create message templates (appointment confirmation, etc.)
- Set `WHATSAPP_API_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` on Render

### 8. Add Privacy Policy and Terms of Service Pages
**Who:** Prakash (content)
**What:**
- Required for Google OAuth consent screen production verification
- Required for Razorpay merchant onboarding
- Pages should live at `patientplex.ai/privacy` and `patientplex.ai/terms`

### 9. Set Up Redis (Optional but Recommended)
**Who:** Prakash (infra)
**Where:** Render or Upstash
**What:**
- Render Redis add-on or Upstash free tier
- Set `REDIS_URL` on Render
- Enables: proper rate limiting, session store, caching

### 10. Domain DNS
**Who:** Prakash (DNS admin)
**What:**
- Point `patientplex.ai` to Vercel (frontend)
- Point `api.patientplex.ai` to Render (backend)
- Update CORS origins and OAuth redirect URIs to use custom domains
- Update `BACKEND_BASE_URL` and `FRONTEND_BASE_URL`

---

## 🟢 NICE-TO-HAVE — Complete When Resources Allow

### 11. Add Google Analytics 4 Server-Side Tracking
- Set `GA4_API_SECRET` and `GA4_PROPERTY_ID` for Measurement Protocol
- Currently only client-side gtag is configured

### 12. Set Up Google My Business API
- Apply for GMB API access
- Currently returns demo data

### 13. LinkedIn Ads Integration
- Create LinkedIn Marketing Developer App
- Get access token
- Not wired to any router currently

### 14. Set Up Monitoring and Alerting
- Render has basic health checks
- Consider adding Sentry for error tracking
- Consider UptimeRobot for uptime monitoring
