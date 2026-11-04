"""Cal.com API integration for appointment scheduling.

Cal.com is the open-source scheduling infrastructure that replaces
manual Google Calendar management. It provides:
- Programmable booking slots with availability rules
- Built-in conflict detection
- Automatic calendar sync (Google, Outlook)
- Booking confirmations and reminders
- Embeddable booking widget
- Self-hostable for zero infrastructure cost

API docs: https://cal.com/docs/api-reference/v1
"""

import logging
from datetime import datetime, date

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class CalComService:
    """Manages scheduling through Cal.com API.

    Can work with:
    - Cal.com Cloud (api.cal.com) — hosted, pay per booking
    - Self-hosted Cal.com — free, you run the server
    """

    def __init__(self):
        self.base_url = settings.CALCOM_BASE_URL.rstrip("/")
        self.api_key = settings.CALCOM_API_KEY
        self.headers = {"Content-Type": "application/json"}

    def _params(self) -> dict:
        return {"apiKey": self.api_key}

    async def get_available_slots(
        self,
        event_type_id: int | None = None,
        start_date: str = "",
        end_date: str = "",
        timezone: str = "Asia/Kolkata",
    ) -> list[dict]:
        """Get available booking slots for a date range.

        Args:
            event_type_id: Cal.com event type ID (e.g. "30-min consultation")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            timezone: IANA timezone string

        Returns:
            List of available slot dicts with 'time' key (ISO format)
        """
        event_id = event_type_id or settings.CALCOM_EVENT_TYPE_ID
        if not event_id:
            logger.warning("No Cal.com event type configured")
            return []

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/slots",
                    params={
                        **self._params(),
                        "eventTypeId": event_id,
                        "startTime": f"{start_date}T00:00:00.000Z",
                        "endTime": f"{end_date}T23:59:59.000Z",
                        "timeZone": timezone,
                    },
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()

                # Cal.com returns {slots: {date: [slot_times]}}
                slots = []
                for date_key, times in data.get("slots", {}).items():
                    for slot in times:
                        time_str = slot.get("time", slot) if isinstance(slot, dict) else slot
                        slots.append({
                            "start": time_str,
                            "date": date_key,
                        })
                return slots

        except httpx.HTTPError as exc:
            logger.error("Cal.com slots fetch failed: %s", exc)
            return []

    async def create_booking(
        self,
        event_type_id: int | None = None,
        start_time: str = "",
        patient_name: str = "",
        patient_email: str = "",
        patient_phone: str = "",
        treatment: str = "",
        notes: str = "",
        timezone: str = "Asia/Kolkata",
    ) -> dict:
        """Create a booking through Cal.com API.

        This automatically:
        - Blocks the slot on the doctor's calendar
        - Sends confirmation email (if configured in Cal.com)
        - Syncs to Google Calendar / Outlook

        Args:
            event_type_id: Cal.com event type ID
            start_time: ISO format datetime string
            patient_name: Full name of the patient
            patient_email: Patient email (Cal.com requires this)
            patient_phone: Patient phone number
            treatment: Treatment/service description
            notes: Additional notes for the booking

        Returns:
            Booking response with id, uid, startTime, endTime
        """
        event_id = event_type_id or settings.CALCOM_EVENT_TYPE_ID
        if not event_id:
            return {"error": "No Cal.com event type configured"}

        payload = {
            "eventTypeId": event_id,
            "start": start_time,
            "responses": {
                "name": patient_name,
                "email": patient_email or f"{patient_phone}@patientplex.ai",
                "phone": patient_phone,
                "notes": f"Treatment: {treatment}. {notes}".strip(),
            },
            "timeZone": timezone,
            "language": "en",
            "metadata": {
                "source": "patientplex",
                "treatment": treatment,
                "phone": patient_phone,
            },
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/bookings",
                    params=self._params(),
                    json=payload,
                    headers=self.headers,
                    timeout=15,
                )
                resp.raise_for_status()
                booking = resp.json()

                logger.info(
                    "Cal.com booking created: %s for %s at %s",
                    booking.get("uid", "?"), patient_name, start_time,
                )
                return {
                    "success": True,
                    "booking_id": booking.get("id"),
                    "booking_uid": booking.get("uid"),
                    "start_time": booking.get("startTime"),
                    "end_time": booking.get("endTime"),
                    "status": booking.get("status", "ACCEPTED"),
                }

        except httpx.HTTPError as exc:
            logger.error("Cal.com booking failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def cancel_booking(self, booking_id: int, reason: str = "") -> dict:
        """Cancel an existing Cal.com booking."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.delete(
                    f"{self.base_url}/bookings/{booking_id}",
                    params={**self._params(), "cancellationReason": reason},
                    timeout=10,
                )
                resp.raise_for_status()
                return {"success": True, "cancelled": True}
        except httpx.HTTPError as exc:
            logger.error("Cal.com cancel failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def reschedule_booking(
        self, booking_uid: str, new_start: str, reason: str = ""
    ) -> dict:
        """Reschedule an existing booking to a new time."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(
                    f"{self.base_url}/bookings/{booking_uid}",
                    params=self._params(),
                    json={
                        "start": new_start,
                        "rescheduleReason": reason,
                    },
                    headers=self.headers,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "success": True,
                    "new_start": data.get("startTime"),
                    "new_end": data.get("endTime"),
                }
        except httpx.HTTPError as exc:
            logger.error("Cal.com reschedule failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def get_event_types(self) -> list[dict]:
        """List all event types (appointment types) configured in Cal.com.

        Use this during onboarding to let doctors pick which services
        to offer for booking.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.base_url}/event-types",
                    params=self._params(),
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                return [
                    {
                        "id": et.get("id"),
                        "title": et.get("title"),
                        "slug": et.get("slug"),
                        "length": et.get("length"),  # Duration in minutes
                        "description": et.get("description"),
                    }
                    for et in data.get("event_types", [])
                ]
        except httpx.HTTPError as exc:
            logger.error("Cal.com event types fetch failed: %s", exc)
            return []

    async def create_event_type(
        self,
        title: str,
        slug: str,
        duration_minutes: int = 30,
        description: str = "",
    ) -> dict:
        """Create a new event type (e.g. 'Braces Consultation - 30 min').

        Called during doctor onboarding to set up their appointment types.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/event-types",
                    params=self._params(),
                    json={
                        "title": title,
                        "slug": slug,
                        "length": duration_minutes,
                        "description": description,
                    },
                    headers=self.headers,
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "success": True,
                    "event_type_id": data.get("id"),
                    "slug": data.get("slug"),
                }
        except httpx.HTTPError as exc:
            logger.error("Cal.com event type creation failed: %s", exc)
            return {"success": False, "error": str(exc)}


calcom_service = CalComService()
