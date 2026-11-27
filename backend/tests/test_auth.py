"""Tests for authentication endpoints."""

import pytest


@pytest.mark.asyncio
async def test_signup_success(client):
    resp = await client.post("/api/v1/auth/signup", json={
        "full_name": "Dr. Signup Test",
        "email": "signup@test.com",
        "phone": "+919234567890",
        "password": "Pass123!",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    payload = {
        "full_name": "Dr. Dup",
        "email": "dup@test.com",
        "phone": "+919111111111",
        "password": "Pass123!",
    }
    first = await client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    # Signup first
    await client.post("/api/v1/auth/signup", json={
        "full_name": "Dr. Login",
        "email": "login@test.com",
        "phone": "+919222222222",
        "password": "Pass123!",
    })
    # Login
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@test.com",
        "password": "Pass123!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/signup", json={
        "full_name": "Dr. Wrong",
        "email": "wrong@test.com",
        "phone": "+919333333333",
        "password": "Correct123!",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrong@test.com",
        "password": "WrongPassword!",
    })
    assert resp.status_code in (400, 401)


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Dr. Test Kumar"
    assert data["email"].endswith("@patientplex.ai")


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_signup_rejects_invalid_indian_phone(client):
    resp = await client.post('/api/v1/auth/signup', json={'full_name': 'Synthetic Doctor', 'email': 'invalid-phone@example.com', 'phone': '+911234567890', 'password': 'Pass123!'})
    assert resp.status_code == 422
