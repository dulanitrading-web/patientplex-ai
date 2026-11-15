# PatientPlex AI — Integration Setup Guide

## Prerequisites

- Render backend deployed at: `https://patientplex-ai-g7ce.onrender.com`
- Vercel frontend deployed at: `https://patientplex-ai.vercel.app`
- PostgreSQL database provisioned on Render
- All environment variables set (see Environment Variables section)

---

## 1. Google Ads Integration

### What You Need
- Google Ads account (MCC or individual)
- Google Cloud Console project with OAuth configured
- Google Ads API developer token (apply at https://ads.google.com/nav/account)

### Setup Steps

1. **Google Cloud Console** (https://console.cloud.google.com)
   - Create project or use existing (`bdc-agent-507019`)
   - Enable "Google Ads API"
   - Create OAuth 2.0 credentials (Web application type)
   - Add authorized redirect URIs:
     - `https://patientplex-ai-g7ce.onrender.com/api/v1/integrations/google-ads/callback`
   - **IMPORTANT:** Publish OAuth consent screen to "Production" (currently in "Testing" mode)

2. **Render Environment Variables**
   ```
   GOOGLE_CLIENT_ID=<from Google Cloud Console>
   GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
   GOOGLE_ADS_DEVELOPER_TOKEN=<from Google Ads API Center>
   GOOGLE_ADS_LOGIN_CUSTOMER_ID=<MCC customer ID, no dashes>
   ```

3. **Per-Clinic Connection**
   - Clinic owner clicks "Connect" on Settings → Google Ads
   - Redirected to Google OAuth consent screen
   - Authorizes PatientPlex to manage their ads
   - Refresh token stored (encrypted) in doctor record
   - Customer ID auto-detected

4. **Import Campaigns**
   - After connecting, click "Import Campaigns"
   - Uses Google Ads REST API v17 (no SDK needed)
   - Imports existing campaigns with metrics

### Current Status
- OAuth flow: ✅ Working
- REST API: ✅ Implemented (no SDK dependency)
- Import: ⚠️ Deployed but needs production testing
- OAuth consent: ❌ Still in "Testing" mode — only 1 test user can authorize

---

## 2. Meta (Facebook) Ads Integration

### What You Need
- Facebook Business account
- Meta App on developers.facebook.com
- Ad account access

### Setup Steps

1. **Meta for Developers** (https://developers.facebook.com)
   - Create app (Business type)
   - Add "Marketing API" product
   - Note App ID and App Secret

2. **Render Environment Variables**
   ```
   META_APP_ID=<Facebook App ID>
   META_APP_SECRET=<Facebook App Secret>
   ```

3. **Per-Clinic Connection**
   - Clinic clicks "Connect" on Settings → Meta Ads
   - Redirected to Facebook OAuth
   - Authorizes ad management + page access
   - Long-lived token (60 days) stored encrypted
   - Ad account and page auto-detected

### Current Status
- OAuth flow: ✅ Implemented
- Token exchange: ✅ Short → long-lived token
- Campaign creation: ⚠️ Engine exists but untested with real account
- Ad account: ⚠️ Auto-selects first account (may not be correct for multi-account users)

---

## 3. Google Calendar Integration

### What You Need
- Google Cloud Console project (same as Google Ads)
- Calendar API enabled

### Setup Steps

1. **Google Cloud Console**
   - Enable "Google Calendar API"
   - Add redirect URI:
     - `https://patientplex-ai-g7ce.onrender.com/api/v1/onboarding/google-calendar/callback`

2. **Render Environment Variables**
   ```
   GOOGLE_CLIENT_ID=<same as Google Ads>
   GOOGLE_CLIENT_SECRET=<same as Google Ads>
   GOOGLE_REDIRECT_URI=https://patientplex-ai-g7ce.onrender.com/api/v1/onboarding/google-calendar/callback
   ```

3. **Connection**
   - During onboarding or from Settings, click "Connect Google Calendar"
   - Authorize calendar access
   - Token stored in `google_calendar_token` JSON column

### Current Status
- OAuth flow: ✅ Working
- Appointment sync: ✅ Implemented
- Token: ⚠️ Stored unencrypted (JSON column) — needs encryption migration

---

## 4. WhatsApp Business API

### What You Need
- Meta Business account
- WhatsApp Business API access
- Phone number verified on WhatsApp Business

### Setup Steps

1. **Meta Business** (https://business.facebook.com)
   - Set up WhatsApp Business API
   - Get Phone Number ID and permanent access token
   - Create message templates

2. **Render Environment Variables**
   ```
   WHATSAPP_API_TOKEN=<permanent access token>
   WHATSAPP_PHONE_NUMBER_ID=<phone number ID>
   WHATSAPP_VERIFY_TOKEN=<webhook verification token>
   ```

3. **Verification**
   - Clinic enters WhatsApp number during onboarding
   - Click "Verify" on Settings page
   - Test message sent via Cloud API

### Current Status
- API client: ✅ Implemented
- Verification: ⚠️ Token format parsing fragile
- AI receptionist: ✅ Claude-powered responses
- Templates: ❌ Need to create approved templates

---

## 5. Twilio Voice & SMS

### What You Need
- Twilio account (paid, not trial)
- Indian phone number capability (or US fallback)

### Setup Steps

1. **Twilio Console** (https://console.twilio.com)
   - Upgrade from trial to paid account
   - Enable India number provisioning (requires business verification)

2. **Render Environment Variables**
   ```
   TWILIO_ACCOUNT_SID=<Account SID>
   TWILIO_AUTH_TOKEN=<Auth Token>
   TWILIO_WHATSAPP_NUMBER=<Twilio WhatsApp number>
   ```

3. **Number Provisioning**
   - Click "Provision Number" in Settings
   - System tries India first, falls back to US
   - Number used in Google Ads call extensions

### Current Status
- Integration: ✅ Implemented
- Number provisioning: ⚠️ Blocked on trial accounts
- Call tracking: ✅ Webhook handler exists
- WhatsApp via Twilio: ⚠️ Sandbox only

---

## 6. Razorpay Payments

### What You Need
- Razorpay account (https://razorpay.com)
- KYC completed
- Test mode keys for development

### Setup Steps

1. **Razorpay Dashboard**
   - Get API Key ID and Key Secret
   - Note test vs live keys

2. **Render Environment Variables**
   ```
   RAZORPAY_KEY_ID=<Key ID>
   RAZORPAY_KEY_SECRET=<Key Secret>
   ```

3. **Frontend** (NOT YET IMPLEMENTED)
   - Load Razorpay checkout SDK
   - Call backend to create order
   - Open Razorpay checkout modal
   - Verify payment on success

### Current Status
- Backend endpoints: ✅ Create order + verify payment
- Frontend checkout: ❌ Not implemented — no way for users to pay
- Plans: ₹9,999 / ₹24,999 / ₹49,999 per month

---

## Environment Variables Checklist

| Variable | Required | Set on Render |
|----------|----------|---------------|
| DATABASE_URL | ✅ | ✅ |
| SECRET_KEY | ✅ | ✅ |
| ENCRYPTION_KEY | ✅ | ✅ |
| ENVIRONMENT | ✅ | ✅ |
| BACKEND_BASE_URL | ✅ | ❌ (uses default) |
| FRONTEND_BASE_URL | ✅ | ❌ (uses default) |
| GOOGLE_CLIENT_ID | ✅ | ✅ |
| GOOGLE_CLIENT_SECRET | ✅ | ✅ |
| GOOGLE_REDIRECT_URI | ✅ | ✅ |
| GOOGLE_ADS_DEVELOPER_TOKEN | ✅ | ✅ |
| GOOGLE_ADS_LOGIN_CUSTOMER_ID | ✅ | ✅ |
| META_APP_ID | ✅ | ✅ |
| META_APP_SECRET | ✅ | ✅ |
| TWILIO_ACCOUNT_SID | ✅ | ✅ |
| TWILIO_AUTH_TOKEN | ✅ | ✅ |
| WHATSAPP_API_TOKEN | For WhatsApp | ❌ |
| RAZORPAY_KEY_ID | For payments | ❓ |
| RAZORPAY_KEY_SECRET | For payments | ❓ |
| CLAUDE_API_KEY | For AI features | ✅ |
| REDIS_URL | For caching | ❌ (no Redis) |
