import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.booking_engine import BookingEngine


def test_unavailable_slot_does_not_create_booking():
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    engine = BookingEngine(db)
    engine.check_availability = AsyncMock(return_value={"slots": []})
    engine.calendar.book_slot = AsyncMock()
    doctor = MagicMock(id=uuid4())
    response = asyncio.run(engine.book_appointment(
        doctor, "Synthetic", "0000000000", "Consultation", "2030-01-01", "10:00"
    ))
    assert response["success"] is False
    engine.calendar.book_slot.assert_not_awaited()
    db.commit.assert_not_awaited()


def test_connected_calendar_failure_does_not_invent_slots():
    engine = BookingEngine(AsyncMock())
    engine.calendar.get_available_slots = AsyncMock(side_effect=RuntimeError("offline"))
    doctor = MagicMock(id=uuid4(), google_calendar_connected=True)
    response = asyncio.run(engine.check_availability(doctor, "2030-01-01"))
    assert response["available"] is False
    assert response["slots"] == []
