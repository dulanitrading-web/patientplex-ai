"""Regression tests using synthetic inputs and mocked database access."""
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.leads import LeadCaptureRequest, capture_lead


@pytest.mark.parametrize("fields,status", [
    ({}, 422),
    ({"doctor_id": "invalid"}, 422),
    ({"doctor_id": str(uuid4())}, 404),
    ({"doctor_slug": "unknown-clinic"}, 404),
])
def test_invalid_routing_rejected(fields, status):
    db = AsyncMock()
    db.get.return_value = None
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    body = LeadCaptureRequest(patient_name="Synthetic", patient_phone="0000000000", **fields)
    with pytest.raises(HTTPException) as error:
        asyncio.run(capture_lead(body, MagicMock(), db))
    assert error.value.status_code == status
    db.commit.assert_not_awaited()


def test_conflicting_clinic_identifiers_rejected():
    db = AsyncMock()
    db.get.return_value = MagicMock(id=uuid4())
    result = MagicMock()
    result.scalar_one_or_none.return_value = MagicMock(id=uuid4())
    db.execute.return_value = result
    body = LeadCaptureRequest(
        patient_name="Synthetic", patient_phone="0000000000",
        doctor_id=str(db.get.return_value.id), doctor_slug="other-clinic",
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(capture_lead(body, MagicMock(), db))
    assert error.value.status_code == 422
    db.commit.assert_not_awaited()
