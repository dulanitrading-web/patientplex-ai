# PatientPlex AI — Deploy in 30 Minutes

## What you need BEFORE starting

### Free accounts (sign up now, takes 10 minutes):

| Service | URL | What you get free | What you need from it |
|---------|-----|-------------------|----------------------|
| **Twilio** | twilio.com/try-twilio | $15 trial credit | Account SID, Auth Token, Phone Number |
| **Claude API** | console.anthropic.com | $5 free credit | API Key |
| **Cal.com** | cal.com | Free forever plan | API Key (Settings → Developer → API Keys) |
| **VPS** | railway.app OR render.com | Free tier available | Server to deploy on |

### Optional (not needed for first doctor):
- Google Cloud Console (for Google Calendar OAuth) — can use Cal.com instead
- Meta Developer Account (for WhatsApp Cloud API) — can use Twilio WhatsApp sandbox first
- Razorpay (for billing) — not needed until you charge money

---

## Step 1: Get your API keys (10 minutes)

### Twilio (missed call detection + WhatsApp)
1. Go to twilio.com/try-twilio → sign up
2. Dashboard shows: **Account SID** and **Auth Token** — copy both
3. Buy a phone number: Console → Phone Numbers → Buy a Number → pick any number ($1 from trial credit)
4. For WhatsApp sandbox: Console → Messaging → Try it out → Send a WhatsApp message → follow the instructions to join sandbox

### Claude API (AI receptionist)
1. Go to console.anthropic.com → sign up
2. API Keys → Create Key → copy it
3. You get $5 free credit (enough for ~500 patient conversations)

### Cal.com (appointment scheduling)
1. Go to cal.com → sign up free
2. Set up one Event Type: "Doctor Appointment" → 30 min → set available hours
3. Settings → Developer → API Keys → Create → copy it
4. Note your Event Type ID (shown in URL when you click on it)

---

## Step 2: Deploy on Railway (10 minutes, free tier)

### Option A: Railway (easiest, free tier)

1. Go to railway.app → sign up with GitHub
2. Push the code to your GitHub first:
```bash
cd cliniccare
git init
git add -A
git commit -m "PatientPlex AI v1"
# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/patientplex-ai.git
git push -u origin main
```

3. In Railway:
   - New Project → Deploy from GitHub repo → select your repo
   - Add a PostgreSQL database (click + New → Database → PostgreSQL)
   - Railway auto-detects Docker and deploys

4. Set environment variables in Railway dashboard:
```
DATABASE_URL=<Railway gives you this automatically>
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
CLAUDE_API_KEY=<from step 1>
TWILIO_ACCOUNT_SID=<from step 1>
TWILIO_AUTH_TOKEN=<from step 1>
TWILIO_PHONE_NUMBER=<your Twilio number like +1234567890>
TWILIO_WHATSAPP_NUMBER=<Twilio WhatsApp sandbox number>
CALCOM_API_KEY=<from step 1>
CALCOM_BASE_URL=https://api.cal.com/v1
CALCOM_EVENT_TYPE_ID=<your event type ID>
WHATSAPP_API_TOKEN=<same as Twilio auth token for now>
GOOGLE_CLIENT_ID=<leave empty for now>
GOOGLE_CLIENT_SECRET=<leave empty for now>
META_APP_ID=<leave empty for now>
META_APP_SECRET=<leave empty for now>
```

5. After deploy, run the database setup:
   - Railway → your service → Settings → Run command:
   ```
   python create_tables.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```

### Option B: Any VPS with Docker (DigitalOcean, AWS, etc.)

```bash
# SSH into your server
ssh root@your-server-ip

# Clone your code
git clone https://github.com/YOUR_USERNAME/patientplex-ai.git
cd patientplex-ai

# Create .env file
cat > .env << 'EOF'
POSTGRES_USER=patientplex
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE
POSTGRES_DB=patientplex
SECRET_KEY=YOUR_SECRET_KEY_HERE
CLAUDE_API_KEY=YOUR_KEY
TWILIO_ACCOUNT_SID=YOUR_SID
TWILIO_AUTH_TOKEN=YOUR_TOKEN
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+14155238886
CALCOM_API_KEY=YOUR_KEY
CALCOM_BASE_URL=https://api.cal.com/v1
WHATSAPP_API_TOKEN=YOUR_TOKEN
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/onboarding/google-calendar/callback
META_APP_ID=
META_APP_SECRET=
API_URL=https://yourdomain.com/api/v1
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up --build -d

# Create database tables
docker-compose -f docker-compose.prod.yml exec backend python create_tables.py

# Check it's running
curl http://localhost:8000/
# Should return: {"status":"healthy","service":"PatientPlex AI"}
```

---

## Step 3: Connect Twilio webhooks (5 minutes)

1. Go to Twilio Console → Phone Numbers → your number → Configure
2. Set Voice webhook:
   - **When a call comes in:** `https://YOUR-DOMAIN/api/v1/calls/incoming` (HTTP POST)
   - **Status callback URL:** `https://YOUR-DOMAIN/api/v1/calls/status` (HTTP POST)
3. Set Messaging webhook (for WhatsApp):
   - **When a message comes in:** `https://YOUR-DOMAIN/api/v1/whatsapp/webhook` (HTTP POST)

---

## Step 4: Test it yourself (5 minutes)

1. Open `https://YOUR-DOMAIN` in browser → you should see PatientPlex AI
2. Sign up as a doctor → complete onboarding
3. Call your Twilio number from your personal phone → don't answer
4. Within 30 seconds, you should get a WhatsApp message
5. Reply to the WhatsApp → AI should offer appointment slots
6. Book a slot → check that Cal.com shows the booking

---

## Step 5: Onboard your first real doctor

1. Give the doctor the Twilio phone number
2. Tell them: "Forward your clinic calls to this number when you're busy"
   - Or: use this as the number in Google Ads click-to-call
3. Sign them up on PatientPlex AI dashboard
4. Set their available hours in Cal.com
5. Done — missed calls will now get WhatsApp follow-up automatically

---

## Total cost to run first doctor:

| Item | Cost | Notes |
|------|------|-------|
| Twilio phone number | ~$1/month | From trial credit |
| Twilio calls | ~$0.02/min | From trial credit |
| Twilio WhatsApp | ~$0.005/msg | From trial credit |
| Claude API | ~₹2-3/conversation | From free credit |
| Cal.com | Free | Free plan |
| Railway/VPS | Free-₹500/mo | Free tier or cheapest plan |
| **Total Month 1** | **Under ₹500** | Using free trial credits |

---

## Troubleshooting

**Backend won't start:** Check DATABASE_URL format — must start with `postgresql+asyncpg://`

**WhatsApp not sending:** Check TWILIO_WHATSAPP_NUMBER — for sandbox it's `whatsapp:+14155238886`

**AI not responding:** Check CLAUDE_API_KEY is set and has credit at console.anthropic.com

**Calls not forwarding:** Make sure Twilio webhook URL is correct and your server is publicly accessible (not localhost)

**Database error on startup:** Run `docker-compose exec backend python create_tables.py` again
