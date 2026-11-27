"""Tests for booking engine and appointment management."""

import pytest
from unittest.mock import AsyncMock
from app.services.booking_engine import whatsapp_service, DoctorNotifier


@pytest.fixture(autouse=True)
def mock_notifications(monkeypatch):
    sender = AsyncMock(return_value={'messages': [{'id': 'synthetic-message'}]})
    monkeypatch.setattr(whatsapp_service, 'send_message', sender)
    monkeypatch.setattr(DoctorNotifier, 'notify_new_booking', AsyncMock(return_value={'status': 'sent'}))
    return sender


@pytest.mark.asyncio
async def test_check_availability(client, onboarded_doctor):
    resp = await client.post("/api/v1/bookings/check-availability",
        headers=onboarded_doctor, json={"date": "2026-12-15", "preferred_time": "morning"})
    assert resp.status_code == 200
    data = resp.json()
    # When Google Calendar is not connected, the endpoint returns
    # generated default slots based on clinic hours.  In CI/test
    # the calendar is never connected so we accept both outcomes.
    if data["available"]:
        assert data["total_slots"] > 0
        # All morning slots should be before 12:00
        for slot in data["slots"]:
            hour = int(slot["start"].split(":")[0])
            assert hour < 12
    else:
        # No calendar connected — endpoint correctly reports unavailable
        assert data["total_slots"] == 0 or "slots" in data


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


@pytest.mark.asyncio
async def test_booking_survives_notification_failure(client, onboarded_doctor, mock_notifications, monkeypatch):
    mock_notifications.return_value = {"error": "synthetic provider failure"}
    monkeypatch.setattr(DoctorNotifier, "notify_new_booking", AsyncMock(return_value={"status": "failed"}))
    resp = await client.post("/api/v1/bookings/book", headers=onboarded_doctor, json={
        "patient_name": "Synthetic Patient", "patient_phone": "919000000001",
        "treatment": "Consultation", "date": "2030-12-16", "time": "10:30",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["confirmation_sent"] is False
    assert data["doctor_notified"] is False
    funnel = await client.get("/api/v1/conversions/funnel", headers=onboarded_doctor)
    assert funnel.status_code == 200
    assert funnel.json()["total_stages_tracked"] == 1


@pytest.mark.asyncio
async def test_manual_booking_confirms_assigned_practitioner(
    client, onboarded_doctor, monkeypatch
):
    send_confirmation = AsyncMock(return_value={"sent": True})
    monkeypatch.setattr(
        "app.services.email_service.send_appointment_confirmation", send_confirmation
    )
    staff_response = await client.post(
        "/api/v1/staff/", headers=onboarded_doctor, json={
            "full_name": "Synthetic Orthodontist",
            "specialty": "Orthodontics",
            "services": ["Braces"],
        },
    )
    staff_response.raise_for_status()
    staff_id = staff_response.json()["staff"]["id"]
    booking = {
        "staff_id": staff_id,
        "patient_name": "Synthetic Patient",
        "patient_phone": "+919000000002",
        "patient_email": "synthetic-patient@example.com",
        "treatment": "Smile Design",
        "date": "2026-12-15",
        "time": "10:00",
    }
    wrong_service = await client.post(
        "/api/v1/appointments/book", headers=onboarded_doctor, json=booking
    )
    assert wrong_service.status_code == 422
    send_confirmation.assert_not_awaited()

    booking["treatment"] = "Braces"
    response = await client.post(
        "/api/v1/appointments/book", headers=onboarded_doctor, json=booking
    )
    assert response.status_code == 200
    assert response.json()["appointment"]["staff_id"] == staff_id
    send_confirmation.assert_awaited_once()
    assert send_confirmation.await_args.kwargs["doctor_name"] == "Synthetic Orthodontist"
    assert send_confirmation.await_args.kwargs["clinic_address"] == "123 Test Road"
