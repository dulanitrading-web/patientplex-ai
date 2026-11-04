"""Tests for doctor onboarding flow."""

import pytest


@pytest.mark.asyncio
async def test_get_specialties(client, auth_headers):
    resp = await client.get("/api/v1/onboarding/specialties", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 10
    # Each specialty should have services and keywords
    for spec in data:
        assert "specialty" in spec
        assert "default_services" in spec
        assert len(spec["default_services"]) > 0


@pytest.mark.asyncio
async def test_onboarding_step1(client, auth_headers):
    resp = await client.put("/api/v1/onboarding/step1", headers=auth_headers, json={
        "specialty": "DENTIST",
        "services": ["Root Canal", "Braces"],
        "clinic_name": "My Dental",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["specialty"] == "DENTIST"
    assert data["onboarding_step"] == 2


@pytest.mark.asyncio
async def test_onboarding_step2(client, auth_headers):
    # Must do step 1 first
    await client.put("/api/v1/onboarding/step1", headers=auth_headers, json={
        "specialty": "DENTIST", "services": ["Cleaning"], "clinic_name": "Test",
    })
    resp = await client.put("/api/v1/onboarding/step2", headers=auth_headers, json={
        "clinic_address": "42 Test Street",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "geo_radius_km": 10,
    })
    assert resp.status_code == 200
    assert resp.json()["city"] == "Mumbai"
    assert resp.json()["geo_radius_km"] == 10


@pytest.mark.asyncio
async def test_full_onboarding_flow(client, auth_headers):
    """Complete all 4 steps and verify onboarding completes."""
    # Step 1
    await client.put("/api/v1/onboarding/step1", headers=auth_headers, json={
        "specialty": "DERMATOLOGIST",
        "services": ["Acne Treatment", "Laser"],
        "clinic_name": "Skin Care Clinic",
    })
    # Step 2
    await client.put("/api/v1/onboarding/step2", headers=auth_headers, json={
        "clinic_address": "Road 5, Jubilee Hills",
        "city": "Hyderabad",
        "state": "Telangana",
        "pincode": "500033",
        "geo_radius_km": 7,
    })
    # Step 3
    await client.put("/api/v1/onboarding/step3", headers=auth_headers, json={
        "monthly_budget": 20000,
    })
    # Step 4
    await client.put("/api/v1/onboarding/step4", headers=auth_headers, json={
        "whatsapp_number": "+919876543210",
    })
    # Complete
    resp = await client.post("/api/v1/onboarding/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["onboarding_completed"] is True


@pytest.mark.asyncio
async def test_onboarding_status(client, auth_headers):
    resp = await client.get("/api/v1/onboarding/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "current_step" in data
    assert "steps" in data
