"""Google Calendar integration for reading availability and booking appointments."""

from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.doctor import Doctor

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarService:
    """Manages Google Calendar OAuth, availability checks, and appointment booking."""

    @staticmethod
    def _get_flow() -> Flow:
        """Create a Google OAuth flow with the configured credentials."""
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        return flow

    @staticmethod
    async def _build_service(token_data: dict, db: AsyncSession = None, doctor_id: str = None):
        """Build an authorized Calendar API service from stored token data.

        If ``db`` and ``doctor_id`` are provided and the access token has
        expired, the credentials are refreshed using the stored refresh token
        and the updated token is persisted back to the database.
        """
        creds = Credentials(
            token=token_data["token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )

        # Refresh expired credentials when possible
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request

            creds.refresh(Request())

            # Persist the refreshed token back to the database
            if db is not None and doctor_id is not None:
                result = await db.execute(
                    select(Doctor).where(Doctor.id == doctor_id)
                )
                doctor = result.scalar_one()
                updated_token_data = dict(token_data)
                updated_token_data["token"] = creds.token
                doctor.google_calendar_token = updated_token_data
                await db.flush()

        return build("calendar", "v3", credentials=creds)

    async def get_auth_url(self, doctor_id: str) -> str:
        """Generate a Google OAuth consent URL.

        Args:
            doctor_id: The doctor's UUID, passed as OAuth ``state`` so the
                callback can associate the tokens with the correct account.

        Returns:
            The authorization URL the frontend should redirect the doctor to.
        """
        flow = self._get_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=doctor_id,
        )
        return auth_url

    async def handle_callback(
        self, code: str, doctor_id: str, db: AsyncSession
    ) -> dict:
        """Exchange the OAuth authorization code for tokens and persist them.

        Args:
            code: Authorization code returned by Google.
            doctor_id: UUID of the doctor to store the tokens against.
            db: Active database session.

        Returns:
            A dict with ``calendar_id`` and ``connected`` status.
        """
        flow = self._get_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials

        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        # Fetch the primary calendar ID
        service = build("calendar", "v3", credentials=credentials)
        calendar = service.calendars().get(calendarId="primary").execute()
        calendar_id = calendar.get("id", "primary")

        # Persist to database
        result = await db.execute(
            select(Doctor).where(Doctor.id == doctor_id)
        )
        doctor = result.scalar_one()
        doctor.google_calendar_token = token_data
        doctor.google_calendar_id = calendar_id
        doctor.google_calendar_connected = True
        await db.commit()
        await db.refresh(doctor)

        return {"calendar_id": calendar_id, "connected": True}

    async def get_available_slots(
        self, doctor_id: str, date: str, db: AsyncSession
    ) -> list[dict]:
        """Return 30-minute free slots for a given date.

        Reads the doctor's calendar events for the requested day and returns
        the gaps between 9 AM and 8 PM that are at least 30 minutes long.

        Args:
            doctor_id: UUID of the doctor.
            date: Date string in ``YYYY-MM-DD`` format.
            db: Active database session.

        Returns:
            A list of dicts, each with ``start`` and ``end`` ISO timestamps.
        """
        result = await db.execute(
            select(Doctor).where(Doctor.id == doctor_id)
        )
        doctor = result.scalar_one()

        if not doctor.google_calendar_connected or not doctor.google_calendar_token:
            return []

        service = self._build_service(doctor.google_calendar_token)
        calendar_id = doctor.google_calendar_id or "primary"

        # Define working hours: 9:00 AM to 8:00 PM IST (UTC+5:30)
        ist = timezone(timedelta(hours=5, minutes=30))
        day_start = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=9, minute=0, second=0, tzinfo=ist
        )
        day_end = day_start.replace(hour=20, minute=0)

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=day_start.isoformat(),
            timeMax=day_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])

        # Collect busy periods
        busy_periods: list[tuple[datetime, datetime]] = []
        for event in events:
            start = event["start"].get("dateTime")
            end = event["end"].get("dateTime")
            if start and end:
                busy_periods.append(
                    (datetime.fromisoformat(start), datetime.fromisoformat(end))
                )
        busy_periods.sort(key=lambda p: p[0])

        # Compute free 30-minute slots
        slot_duration = timedelta(minutes=30)
        free_slots: list[dict] = []
        current = day_start

        for busy_start, busy_end in busy_periods:
            while current + slot_duration <= busy_start:
                free_slots.append(
                    {
                        "start": current.isoformat(),
                        "end": (current + slot_duration).isoformat(),
                    }
                )
                current += slot_duration
            if busy_end > current:
                current = busy_end

        # Remaining slots after last busy period
        while current + slot_duration <= day_end:
            free_slots.append(
                {
                    "start": current.isoformat(),
                    "end": (current + slot_duration).isoformat(),
                }
            )
            current += slot_duration

        return free_slots

    async def book_slot(
        self,
        doctor_id: str,
        slot_start: datetime,
        patient_name: str,
        patient_phone: str,
        treatment: str,
        db: AsyncSession,
    ) -> dict:
        """Create a calendar event for a patient appointment.

        Args:
            doctor_id: UUID of the doctor.
            slot_start: Start time of the booked slot (timezone-aware).
            patient_name: Name of the patient.
            patient_phone: Patient's phone number.
            treatment: Treatment or service being booked.
            db: Active database session.

        Returns:
            A dict with ``event_id``, ``start``, ``end``, and ``summary``.

        Raises:
            ValueError: If the doctor's Google Calendar is not connected.
        """
        result = await db.execute(
            select(Doctor).where(Doctor.id == doctor_id)
        )
        doctor = result.scalar_one()

        if not doctor.google_calendar_connected or not doctor.google_calendar_token:
            raise ValueError("Google Calendar is not connected for this doctor.")

        service = self._build_service(doctor.google_calendar_token)
        calendar_id = doctor.google_calendar_id or "primary"

        slot_end = slot_start + timedelta(minutes=30)
        summary = f"{treatment} — {patient_name}"
        description = (
            f"Patient: {patient_name}\n"
            f"Phone: {patient_phone}\n"
            f"Treatment: {treatment}\n"
            f"Booked via PatientPlex AI"
        )

        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": slot_start.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": slot_end.isoformat(), "timeZone": "Asia/Kolkata"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        created_event = (
            service.events()
            .insert(calendarId=calendar_id, body=event)
            .execute()
        )

        return {
            "event_id": created_event["id"],
            "start": created_event["start"]["dateTime"],
            "end": created_event["end"]["dateTime"],
            "summary": created_event["summary"],
        }


google_calendar_service = GoogleCalendarService()
