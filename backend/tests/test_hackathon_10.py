"""Hackathon Test Suite — 10 critical test scenarios for PatientPlex AI.

Covers: public booking flow, AI chat, AI receptionist brain,
NMC compliance, rate limiting, and health checks.
"""

import uuid
from datetime import date, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient


# ─── 1. Booking page returns doctor profile ───────────────────────────────────

@pytest.mark.asyncio
async def test_booking_page_returns_doctor_profile(client: AsyncClient, onboarded_doctor):
    """Public booking page should expose doctor profile without auth."""
    # Get the doctor's slug from the me endpoint
    me = await client.get("/api/v1/auth/me", headers=onboarded_doctor)
    slug = me.json()["subdomain_slug"]

    resp = await client.get(f"/api/v1/public/book/{slug}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["doctor_name"] == "Dr. Test Kumar"
    assert data["clinic_name"] == "Test Dental"
    assert "Root Canal" in data["services"]
    assert data["city"] == "Hyderabad"


# ─── 2. Booking page returns available slots ──────────────────────────────────

@pytest.mark.asyncio
async def test_booking_page_returns_available_slots(client: AsyncClient, onboarded_doctor):
    """Availability endpoint should return time slots for a future weekday."""
    me = await client.get("/api/v1/auth/me", headers=onboarded_doctor)
    slug = me.json()["subdomain_slug"]

    # Pick a future weekday (not Sunday)
    target = date.today() + timedelta(days=1)
    while target.weekday() == 6:  # skip Sunday
        target += timedelta(days=1)

    resp = await client.get(
        f"/api/v1/public/book/{slug}/availability",
        params={"date": target.isoformat()},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_slots"] > 0
    assert data["available_slots"] > 0
    # Each slot should have required fields
    slot = data["slots"][0]
    assert "time" in slot
    assert "display" in slot
    assert "available" in slot


# ─── 3. Patient can book an appointment ───────────────────────────────────────

@pytest.mark.asyncio
async def test_patient_can_book_appointment(client: AsyncClient, onboarded_doctor):
    """Full booking flow: get profile → get slots → book appointment."""
    me = await client.get("/api/v1/auth/me", headers=onboarded_doctor)
    slug = me.json()["subdomain_slug"]

    # Find a future weekday
    target = date.today() + timedelta(days=2)
    while target.weekday() == 6:
        target += timedelta(days=1)

    # Book
    resp = await client.post(f"/api/v1/public/book/{slug}/book", json={
        "patient_name": "Ravi Sharma",
        "patient_phone": "+919876543210",
        "patient_email": "ravi@example.com",
        "treatment": "Root Canal",
        "date": target.isoformat(),
        "time": "10:00",
        "source": "Google Ads",
        "utm_source": "google",
        "utm_campaign": "dental_indore",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["appointment"]["treatment"] == "Root Canal"
    assert data["appointment"]["doctor_name"] == "Dr. Test Kumar"


# ─── 4. Booking is rate-limited (conceptual — rate limiter disabled in tests) ─

@pytest.mark.asyncio
async def test_booking_rate_limit_disabled_in_test_mode(client: AsyncClient, onboarded_doctor):
    """Rate limiter should be disabled when TESTING=true (confirmed by env flag)."""
    import os
    assert os.environ.get("TESTING", "").lower() == "true"

    me = await client.get("/api/v1/auth/me", headers=onboarded_doctor)
    slug = me.json()["subdomain_slug"]

    target = date.today() + timedelta(days=3)
    while target.weekday() == 6:
        target += timedelta(days=1)

    # Fire 6 requests in a row — all should succeed because rate limiter is off
    for i in range(6):
        resp = await client.post(f"/api/v1/public/book/{slug}/book", json={
            "patient_name": f"Patient {i}",
            "patient_phone": f"+9199000000{i:02d}",
            "treatment": "Cleaning",
            "date": target.isoformat(),
            "time": f"{10 + i}:00",
        })
        assert resp.status_code == 200, f"Request {i} failed: {resp.text}"


# ─── 5. AI chat responds to greeting ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_ai_chat_responds_to_greeting(client: AsyncClient, onboarded_doctor):
    """AI chat should return a friendly greeting with the doctor's name."""
    resp = await client.post(
        "/api/v1/ai-chat/message",
        headers=onboarded_doctor,
        json={"message": "hello"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    reply_lower = data["reply"].lower()
    # Should greet back — either Claude or rule-based
    assert any(w in reply_lower for w in ["namaste", "hello", "hey", "hi", "help", "assist"])


# ─── 6. AI chat medical guardrail ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ai_chat_medical_guardrail(client: AsyncClient, onboarded_doctor):
    """AI chat should refuse direct medical advice and suggest a doctor consultation."""
    resp = await client.post(
        "/api/v1/ai-chat/message",
        headers=onboarded_doctor,
        json={"message": "What should I do for severe tooth pain? Which medicine should I take?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    reply_lower = data["reply"].lower()
    # Should deflect medical advice
    assert any(w in reply_lower for w in ["consult", "doctor", "medical", "appointment", "clinic management"])


# ─── 7. AI receptionist intent classification ─────────────────────────────────

@pytest.mark.asyncio
async def test_ai_receptionist_intent_classification():
    """Intent classifier should correctly categorise patient messages."""
    from app.services.ai_receptionist import classify_intent, PatientIntent

    cases = [
        ("I want to book an appointment", PatientIntent.BOOKING),
        ("appointment book karna hai", PatientIntent.BOOKING),
        ("How much does root canal cost?", PatientIntent.PRICING),
        ("kitna lagega?", PatientIntent.PRICING),
        ("Where is the clinic?", PatientIntent.DIRECTIONS),
        ("kahan hai clinic?", PatientIntent.DIRECTIONS),
        ("cancel my appointment", PatientIntent.CANCEL),
        ("I'm having severe bleeding right now", PatientIntent.EMERGENCY),
        ("bahut dard ho raha hai", PatientIntent.EMERGENCY),
        ("hello", PatientIntent.GREETING),
        ("namaste", PatientIntent.GREETING),
        ("bad experience at clinic", PatientIntent.COMPLAINT),
        ("Can you reschedule to Monday?", PatientIntent.RESCHEDULE),
    ]
    for message, expected in cases:
        result = classify_intent(message)
        assert result == expected, f"'{message}' → {result}, expected {expected}"


# ─── 8. AI receptionist urgency detection ─────────────────────────────────────

@pytest.mark.asyncio
async def test_ai_receptionist_urgency_detection():
    """Urgency detector should flag emergency messages correctly."""
    from app.services.ai_receptionist import detect_urgency

    urgent_messages = [
        "I have severe bleeding from my gums",
        "emergency - broke my tooth",
        "bahut dard ho raha hai, kha nahi pa raha",
        "accident happened, face injury",
    ]
    safe_messages = [
        "I want to book a cleaning",
        "What are your timings?",
        "kitna lagega root canal?",
        "hello doctor",
    ]

    for msg in urgent_messages:
        assert detect_urgency(msg) is True, f"Should be urgent: '{msg}'"

    for msg in safe_messages:
        assert detect_urgency(msg) is False, f"Should NOT be urgent: '{msg}'"


# ─── 9. NMC compliance blocks superlatives ────────────────────────────────────

@pytest.mark.asyncio
async def test_nmc_compliance_blocks_superlatives():
    """NMC compliance checker should flag superlative claims in ad copy."""
    from app.services.nmc_compliance import check_ad_compliance

    # Non-compliant ad copy
    result = check_ad_compliance("Visit the best dentist in Indore! #1 clinic with guaranteed painless treatment.")
    assert result["compliant"] is False
    assert len(result["violations"]) >= 2  # "best", "#1", "guaranteed", "painless treatment"

    # Compliant ad copy
    result_ok = check_ad_compliance(
        "Visit Bhardwaj Dental Clinic in Indore. Experienced dentist offering root canal, braces, and cleaning. Open Mon-Sat 9AM-8PM."
    )
    assert result_ok["compliant"] is True
    assert len(result_ok["violations"]) == 0


# ─── 10. Health check returns OK ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check_returns_ok(client: AsyncClient):
    """Health check endpoint should respond with healthy status."""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data

    # Lightweight probe creates its own DB session (not through DI),
    # so in SQLite test mode it may return 503 — just verify it responds.
    resp2 = await client.get("/health")
    assert resp2.status_code in (200, 503)
    assert "ok" in resp2.json()
