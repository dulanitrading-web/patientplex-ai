"""Regression tests for clinic-scoped campaign listing (ADS-01 campaign-visibility bug).

Root cause: the Campaigns router was mounted only when ``ADS_ENABLED`` was true,
and the frontend collapsed any request error into an empty list. A signed-in
clinic could sync 23 campaigns via the (always-mounted) integrations router yet
``GET /campaigns/`` returned 404 -> "No campaigns yet".

Covered scenarios (synthetic data only, no provider calls):
- authenticated clinic-scoped listing is always available
- a failed request is NOT reported as an empty clinic
- an empty clinic returns a successful, empty list
- synced campaigns are listed with metrics + sync time
- ad publishing / budget writes remain gated on ADS_ENABLED
- two synthetic clinics are isolated from each other
"""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import get_db
from app.main import app
from app.models.campaign import AdPlatform, Campaign, CampaignStatus
from app.models.doctor import Doctor

API = "/api/v1"


async def _signup(client: AsyncClient, email: str) -> tuple[dict, str]:
    resp = await client.post(
        f"{API}/auth/signup",
        json={
            "full_name": "Synthetic Clinician",
            "email": email,
            "phone": "+919000000000",
            "password": "SyntheticTest123!",
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get(f"{API}/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    return headers, me.json()["id"]


async def _add_campaign(db, doctor_id: str, name: str, **kw) -> Campaign:
    c = Campaign(
        id=uuid.uuid4(),
        doctor_id=uuid.UUID(doctor_id),
        platform=kw.get("platform", AdPlatform.GOOGLE),
        name=name,
        status=kw.get("status", CampaignStatus.ACTIVE),
        campaign_type=kw.get("campaign_type", "SEARCH"),
        daily_budget=kw.get("daily_budget", 500),
        total_budget=kw.get("total_budget", 15000),
        currency="INR",
        impressions=kw.get("impressions", 100),
        clicks=kw.get("clicks", 10),
        conversions=kw.get("conversions", 2),
        spend=kw.get("spend", 250),
        cpc=kw.get("cpc", 25.0),
        ctr=kw.get("ctr", 10.0),
        last_synced_at=kw.get("last_synced_at"),
        created_at=kw.get("created_at", datetime.now(timezone.utc)),
    )
    db.add(c)
    await db.commit()
    return c


@pytest.mark.asyncio
async def test_list_campaigns_requires_auth(client):
    resp = await client.get(f"{API}/campaigns/")
    assert resp.status_code == 401
    # specifically NOT a 404 (router is always mounted) and NOT an empty list
    assert resp.status_code != 404


@pytest.mark.asyncio
async def test_empty_clinic_returns_successful_empty_list(client, db_session):
    headers, _ = await _signup(client, "empty@synthetic.example.com")
    resp = await client.get(f"{API}/campaigns/", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["campaigns"] == []
    assert body["count"] == 0
    # empty is distinct from disabled
    assert isinstance(body.get("ads_enabled"), bool)


@pytest.mark.asyncio
async def test_synced_campaigns_listed_with_metrics_and_sync_time(client, db_session):
    headers, doctor_id = await _signup(client, "synced@synthetic.example.com")
    synced_at = datetime(2026, 11, 27, 8, 0, tzinfo=timezone.utc)
    for i in range(23):
        await _add_campaign(
            db_session, doctor_id, f"Campaign {i}",
            impressions=1000 + i, clicks=50 + i, conversions=i, spend=100 * i,
            last_synced_at=synced_at,
        )

    resp = await client.get(f"{API}/campaigns/", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["count"] == 23
    assert len(body["campaigns"]) == 23
    names = {c["name"] for c in body["campaigns"]}
    assert "Campaign 0" in names and "Campaign 22" in names
    sample = body["campaigns"][0]
    for field in ("impressions", "clicks", "conversions", "spend", "cpc", "ctr",
                  "daily_budget", "status", "platform", "created_at", "last_synced_at"):
        assert field in sample, field
    assert datetime.fromisoformat(sample["last_synced_at"].replace("Z","+00:00")).replace(tzinfo=None) == synced_at.replace(tzinfo=None)
    assert sample["platform"] == "GOOGLE"
    assert sample["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_two_synthetic_clinics_are_isolated(client, db_session):
    a_headers, a_id = await _signup(client, "clinic-a@synthetic.example.com")
    b_headers, b_id = await _signup(client, "clinic-b@synthetic.example.com")

    a_campaign = await _add_campaign(db_session, a_id, "Clinic A Campaign")
    await _add_campaign(db_session, b_id, "Clinic B Campaign")

    # A sees only its own
    a_resp = await client.get(f"{API}/campaigns/", headers=a_headers)
    assert a_resp.status_code == 200
    a_names = {c["name"] for c in a_resp.json()["campaigns"]}
    assert a_names == {"Clinic A Campaign"}
    assert a_resp.json()["count"] == 1

    # B sees only its own
    b_resp = await client.get(f"{API}/campaigns/", headers=b_headers)
    b_names = {c["name"] for c in b_resp.json()["campaigns"]}
    assert b_names == {"Clinic B Campaign"}

    # A cannot read B's campaign by id
    cross = await client.get(f"{API}/campaigns/{a_campaign.id}", headers=b_headers)
    assert cross.status_code == 404

    # listing is not accidentally global
    assert "Clinic B Campaign" not in a_names


@pytest.mark.asyncio
async def test_failed_request_is_not_empty_list(db_session):
    """A backend failure surfaces as 5xx, never as a successful empty list."""
    headers, _ = await _signup_direct(db_session)

    class BoomSession:
        async def execute(self, *a, **k):
            raise RuntimeError("database unavailable")

        async def commit(self):  # pragma: no cover - not reached
            raise RuntimeError("database unavailable")

        async def rollback(self):  # pragma: no cover - not reached
            pass

        async def close(self):  # pragma: no cover - not reached
            pass

    async def override_get_db():
        yield BoomSession()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"{API}/campaigns/", headers=headers)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert resp.status_code >= 500
    assert resp.text != '{"campaigns":[],"count":0}' and resp.text != '{"campaigns": [], "count": 0}'


async def _signup_direct(db_session) -> tuple[dict, str]:
    """Create a doctor row + JWT without going through the signup route."""
    from app.core.security import create_access_token

    doctor = Doctor(
        id=uuid.uuid4(),
        full_name="Synthetic Clinician",
        email=f"boom-{uuid.uuid4().hex[:8]}@synthetic.example.com",
        phone="+919000000000",
        password_hash="x",
    )
    db_session.add(doctor)
    await db_session.commit()
    token = create_access_token({"sub": str(doctor.id)})
    return {"Authorization": f"Bearer {token}"}, str(doctor.id)


@pytest.mark.asyncio
async def test_ad_writes_gated_when_ads_disabled(client, db_session, monkeypatch):
    headers, doctor_id = await _signup(client, "gated@synthetic.example.com")
    campaign = await _add_campaign(db_session, doctor_id, "Gated Campaign")

    import app.api.v1.campaigns as campaigns_mod
    monkeypatch.setattr(campaigns_mod.settings, "ADS_ENABLED", False)

    # listing still works when ads are disabled
    listing = await client.get(f"{API}/campaigns/", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["ads_enabled"] is False
    assert listing.json()["count"] == 1

    # budget write is blocked server-side
    budget = await client.put(
        f"{API}/campaigns/{campaign.id}/budget", headers=headers, json={"daily_budget": 999}
    )
    assert budget.status_code == 403

    # publishing / launch is blocked server-side
    launch = await client.post(f"{API}/campaigns/launch", headers=headers, json={"platforms": ["GOOGLE"]})
    assert launch.status_code == 403
