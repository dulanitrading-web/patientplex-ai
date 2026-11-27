import pytest
from app.core.config import settings

@pytest.mark.asyncio
async def test_webhook_requires_configuration(client, monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET", "")
    response = await client.post("/api/v1/billing/webhook/razorpay", json={"event": "subscription.activated"})
    assert response.status_code == 503

@pytest.mark.asyncio
async def test_webhook_rejects_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET", "synthetic-webhook-secret")
    response = await client.post("/api/v1/billing/webhook/razorpay", json={"event": "subscription.activated"}, headers={"X-Razorpay-Signature": "invalid"})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_paid_plan_cannot_activate_without_payment(client, auth_headers):
    response = await client.post("/api/v1/billing/subscribe", headers=auth_headers, json={"plan": "STARTER"})
    assert response.status_code == 503
    subscription = await client.get("/api/v1/billing/subscription", headers=auth_headers)
    assert subscription.status_code == 200
    sub = subscription.json()["subscription"]
    assert sub is None or sub["plan"] == "FREE_TRIAL"
