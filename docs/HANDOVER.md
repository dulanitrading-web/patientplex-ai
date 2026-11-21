# PatientPlex AI — Developer Handover

> **WARNING:** Earlier handover PDFs shared in chat contained plaintext secrets
> (WhatsApp verify token, Exotel API keys, phone number IDs). Those PDFs should
> be deleted and the `WHATSAPP_VERIFY_TOKEN` rotated on both Render and Meta
> developer console. This file contains NO secret values.

## Status Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Landing page | :green_circle: Live | Vercel, auto-deploys from main |
| Backend API | :green_circle: Live | Render (free tier), 22+ endpoints |
| Doctor onboarding | :green_circle: Working | 4-step wizard |
| Public booking page | :green_circle: Working | Real-time slot availability |
| Patient CRM | :green_circle: Working | Phone/name/source tracked |
| AI receptionist (Groq) | :yellow_circle: Code deployed | Needs WhatsApp API activated |
| Exotel call tracking | :yellow_circle: Code deployed | Blocked: Exotel KYC step 2 |
| WhatsApp messaging | :yellow_circle: Code deployed | Blocked: production number not registered |
| Missed call follow-up | :yellow_circle: Code deployed | Depends on Exotel + WhatsApp |
| Dashboard charts | :red_circle: Not built | API returns data, no charts in UI |
| Razorpay billing | :red_circle: Not built | Config exists, no integration |
| Email notifications | :red_circle: Not configured | Add RESEND_API_KEY |
| Google Ads API | :red_circle: Parked | Code built, no developer token |
| Multi-clinic tenancy | :red_circle: Not built | Single-clinic mode only |

## Live URLs

- **Frontend:** https://patientplex-ai.vercel.app
- **Backend:** https://patientplex-ai-g7ce.onrender.com
- **API docs:** https://patientplex-ai-g7ce.onrender.com/docs
- **Repo:** https://github.com/dulanitrading-web/patientplex-ai

## How to Run Locally

```bash
# Backend
cd backend
cp .env.example .env   # Fill in values — see docs/SECURITY.md for variable list
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev   # localhost:3000
```

## How to Deploy

Push to `main` on GitHub. Both Vercel (frontend) and Render (backend) auto-deploy.

Backend env vars: Render Dashboard → Environment (see docs/SECURITY.md for full list).

## Service Dashboards

| Service | URL | Account |
|---------|-----|---------|
| Render | https://dashboard.render.com/web/srv-dbsb2pk9v7es73c795jg | dulanitrading |
| Vercel | Linked to GitHub repo | — |
| Exotel | https://my.exotel.com/patientplexai1 | patientplexai1 |
| Meta Developer | https://developers.facebook.com/apps/1063669046569296 | — |
| Groq | https://console.groq.com | — |

## Known Blockers (Human Action Required)

### 1. Exotel KYC — Step 2: Business Details
- **What:** Upload Udyam/MSME certificate at https://my.exotel.com/patientplexai1/company_details/#/company-info
- **Why:** ExoPhone 09513886363 cannot receive calls until KYC is approved
- **How:** Register at https://udyamregistration.gov.in (free, needs Aadhaar + PAN for PatientPlex AI)

### 2. WhatsApp Production Number
- **What:** Register 9424488558 on Meta Cloud API
- **Why:** Currently using test number +1 (555) 183-2868
- **How:** On Dr. Anuj's phone → WhatsApp → Settings → Account → Business Platform → enter access code from Meta developer page

### 3. Razorpay KYC
- **What:** Complete Razorpay business verification to accept live payments
- **How:** Sign up at https://dashboard.razorpay.com, complete KYC

### 4. Rotate Leaked Secrets
- **What:** `WHATSAPP_VERIFY_TOKEN` was shared in chat PDFs
- **How:** Generate new token, update on Render AND Meta webhook config simultaneously

## Architecture

```
Patient calls ExoPhone (09513886363)
  → Exotel webhook → /api/v1/calls/exotel/incoming
  → Log call + AI receptionist greeting
  → Forward to doctor's real phone
  → If missed → /api/v1/calls/exotel/status
  → WhatsApp follow-up to patient

Patient sends WhatsApp
  → Meta webhook → /api/v1/whatsapp/webhook
  → AI receptionist (Groq Llama 3.3 70B)
  → Response via Meta Cloud API
  → Can book appointments

Patient visits booking page
  → Selects treatment + slot
  → Backend creates appointment
  → WhatsApp confirmation + reminder
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/core/config.py` | All env var definitions |
| `backend/app/main.py` | FastAPI app, routers, diagnostics |
| `backend/app/services/whatsapp.py` | WhatsApp messaging |
| `backend/app/services/call_tracking.py` | Exotel API client |
| `backend/app/services/call_handler.py` | Call webhook handlers |
| `backend/app/services/ai_receptionist.py` | AI chat (Groq/Claude) |
| `backend/app/services/booking_engine.py` | Appointment slots |
| `backend/app/api/v1/calls.py` | Exotel + Twilio webhook endpoints |
| `backend/app/api/v1/whatsapp.py` | Meta webhook endpoint |
| `frontend/src/app/page.tsx` | Landing page |
| `frontend/src/app/dashboard/` | Doctor dashboard |
