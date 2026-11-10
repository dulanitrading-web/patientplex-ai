"""Shared test fixtures for the PatientPlex AI test suite.

Uses SQLite in-memory database for testing — no PostgreSQL required.
"""

import asyncio
import os
import uuid
import pytest
import pytest_asyncio

# Disable rate limiting for tests — must be set before app import
os.environ["TESTING"] = "true"

from httpx import AsyncClient, ASGITransport
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Import all models so they register with Base.metadata
from app.models.doctor import Doctor  # noqa
from app.models.conversation import Conversation, Appointment  # noqa
from app.models.campaign import Campaign  # noqa
from app.models.call_log import CallLog, ConversionEvent  # noqa
from app.models.billing import Subscription, Invoice  # noqa

# SQLite in-memory — no PostgreSQL needed
TEST_DB_URL = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(eng.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(engine):
    """Wipe all table data between tests for isolation."""
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"DELETE FROM {table.name}"))


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Async HTTP client that uses the test database."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_token(client):
    """Create a test doctor and return their JWT token."""
    unique_email = f"test-{uuid.uuid4().hex[:8]}@patientplex.ai"
    resp = await client.post("/api/v1/auth/signup", json={
        "full_name": "Dr. Test Kumar",
        "email": unique_email,
        "phone": "+919999999999",
        "password": "TestPass123!",
    })
    assert resp.status_code == 201, f"Signup failed: {resp.status_code} {resp.text}"
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def onboarded_doctor(client, auth_headers):
    """A fully onboarded doctor ready for testing."""
    await client.put("/api/v1/onboarding/step1", headers=auth_headers, json={
        "specialty": "DENTIST",
        "services": ["Root Canal", "Braces", "Cleaning"],
        "clinic_name": "Test Dental",
    })
    await client.put("/api/v1/onboarding/step2", headers=auth_headers, json={
        "clinic_address": "123 Test Road",
        "city": "Hyderabad",
        "state": "Telangana",
        "pincode": "500001",
        "geo_radius_km": 5,
    })
    await client.put("/api/v1/onboarding/step3", headers=auth_headers, json={"monthly_budget": 15000})
    await client.put("/api/v1/onboarding/step4", headers=auth_headers, json={"whatsapp_number": "+919999999999"})
    await client.post("/api/v1/onboarding/complete", headers=auth_headers)
    return auth_headers
