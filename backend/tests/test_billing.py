"""Tests for billing and subscription management."""

import pytest


@pytest.mark.asyncio
async def test_list_plans(client):
    resp = await client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()["plans"]
    assert len(plans) == 3  # STARTER, GROWTH, ENTERPRISE
    # Verify pricing
    prices = {p["id"]: p["price_inr"] for p in plans}
    assert prices["STARTER"] == 4999
    assert prices["GROWTH"] == 9999
    assert prices["ENTERPRISE"] == 24999


@pytest.mark.asyncio
async def test_start_trial(client, auth_headers):
    resp = await client.post("/api/v1/billing/start-trial", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["plan"] == "FREE_TRIAL"
    assert resp.json()["trial_ends_at"] is not None


@pytest.mark.asyncio
async def test_get_subscription(client, auth_headers):
    await client.post("/api/v1/billing/start-trial", headers=auth_headers)
    resp = await client.get("/api/v1/billing/subscription", headers=auth_headers)
    assert resp.status_code == 200
    sub = resp.json()["subscription"]
    assert sub["plan"] == "FREE_TRIAL"
    assert sub["status"] == "TRIAL"


@pytest.mark.asyncio
async def test_check_feature_on_trial(client, auth_headers):
    await client.post("/api/v1/billing/start-trial", headers=auth_headers)
    # Conversation should be allowed on trial
    resp = await client.get("/api/v1/billing/check/conversation", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True
    # Meta ads should NOT be allowed on trial
    resp = await client.get("/api/v1/billing/check/META", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


@pytest.mark.asyncio
async def test_upgrade_plan(client, auth_headers):
    await client.post("/api/v1/billing/start-trial", headers=auth_headers)
    resp = await client.post("/api/v1/billing/subscribe", headers=auth_headers, json={"plan": "GROWTH"})
    assert resp.status_code == 200
    assert resp.json()["plan"] == "GROWTH"
    assert resp.json()["price_inr"] == 9999
