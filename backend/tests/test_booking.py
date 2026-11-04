"""Tests for booking engine and appointment management."""

import pytest


@pytest.mark.asyncio
async def test_check_availability(client, onboarded_doctor):
    resp = await client.post("/api/v1/bookings/check-availability",
        headers=onboarded_doctor, json={"date": "2026-12-15", "preferred_time": "morning"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] is True
    assert data["total_slots"] > 0
    # All morning slots should be before 12:00
    for slot in data["slots"]:
        hour = int(slot["start"].split(":")[0])
        assert hour < 12


@pytest.mark.asyncio
async def test_book_appointment(client, onboarded_doctor):
    resp = await client.post("/api/v1/bookings/book", headers=onboarded_doctor, json={
        "patient_name": "Rahul Kumar",
        "patient_phone": "919888777666",
        "treatment": "Braces Consultation",
        "date": "2026-12-16",
        "time": "10:30",
        "source": "test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["patient_name"] == "Rahul Kumar"
    assert data["treatment"] == "Braces Consultation"
    assert data["confirmation_sent"] is True
    assert data["doctor_notified"] is True


@pytest.mark.asyncio
async def test_list_appointments(client, onboarded_doctor):
    # Book one first
    await client.post("/api/v1/bookings/book", headers=onboarded_doctor, json={
        "patient_name": "Test Patient",
        "patient_phone": "919111222333",
        "treatment": "Cleaning",
        "date": "2026-12-17",
        "time": "14:00",
    })
    resp = await client.get("/api/v1/appointments/", headers=onboarded_doctor)
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


@pytest.mark.asyncio
async def test_appointment_stats(client, onboarded_doctor):
    resp = await client.get("/api/v1/appointments/stats?days=30", headers=onboarded_doctor)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_booked" in data
    assert "attendance_rate" in data
    assert "by_treatment" in data


@pytest.mark.asyncio
async def test_conversion_funnel(client, onboarded_doctor):
    # After booking, there should be conversion events
    await client.post("/api/v1/bookings/book", headers=onboarded_doctor, json={
        "patient_name": "Funnel Test",
        "patient_phone": "919444555666",
        "treatment": "Root Canal",
        "date": "2026-12-18",
        "time": "11:00",
    })
    resp = await client.get("/api/v1/conversions/funnel", headers=onboarded_doctor)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_stages_tracked"] >= 2  # BOOKING_CONFIRMED + CONFIRMATION_SENT
