"""Call Tracking Service — provisions virtual numbers and manages calls via Exotel (India) or Twilio (international).

Each clinic gets a virtual number that:
1. Captures the REAL caller's phone number
2. AI receptionist answers and books appointments
3. Forwards calls to the doctor's actual phone
4. Records calls for quality assurance
5. Detects missed calls → triggers WhatsApp AI follow-up
6. Enables callback when a call is missed

Flow:
  Patient calls ExoPhone (from Google Ad / website) →
  Exotel sends webhook to PatientPlex →
  AI receptionist answers, books appointment →
  Forwards call to doctor's phone →
  If missed → WhatsApp follow-up with patient's real number →
  Doctor can see all caller numbers in dashboard + call back
"""

import logging
import os
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Conditionally import Twilio (backup provider)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_SDK_AVAILABLE = True
except ImportError:
    TWILIO_SDK_AVAILABLE = False
    TwilioClient = None


class ExotelService:
    """Exotel API client for Indian call tracking, SMS, and voice."""

    BASE_URL = "https://api.exotel.com/v1/Accounts"

    def __init__(self):
        self.sid = settings.EXOTEL_SID
        self.api_key = settings.EXOTEL_API_KEY
        self.api_token = settings.EXOTEL_API_TOKEN
        self.caller_id = settings.EXOTEL_CALLER_ID  # ExoPhone number
        self._client: httpx.AsyncClient | None = None

        if self.sid and self.api_key and self.api_token:
            logger.info("Exotel configured: SID=%s, ExoPhone=%s", self.sid, self.caller_id)
        else:
            logger.warning("Exotel not configured — set EXOTEL_SID, EXOTEL_API_KEY, EXOTEL_API_TOKEN")

    @property
    def is_connected(self) -> bool:
        return bool(self.sid and self.api_key and self.api_token)

    @property
    def base(self) -> str:
        return f"{self.BASE_URL}/{self.sid}"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                auth=(self.api_key, self.api_token),
                timeout=30.0,
            )
        return self._client

    async def make_call(
        self,
        from_number: str,
        to_number: str,
        caller_id: str | None = None,
        status_callback_url: str | None = None,
    ) -> dict:
        """Initiate an outbound call via Exotel.

        Connects from_number to to_number via the ExoPhone.
        Used for callbacks to patients.
        """
        if not self.is_connected:
            return {"status": "not_configured", "message": "Exotel not configured"}

        exophone = caller_id or self.caller_id
        callback_url = status_callback_url or f"{settings.BACKEND_BASE_URL}/api/v1/calls/exotel/status"

        client = await self._get_client()
        try:
            response = await client.post(
                f"{self.base}/Calls/connect.json",
                data={
                    "From": from_number,
                    "To": to_number,
                    "CallerId": exophone,
                    "Record": "true",
                    "StatusCallback": callback_url,
                    "StatusCallbackEvents[0]": "terminal",
                },
            )
            data = response.json()

            if response.status_code == 200:
                call_data = data.get("Call", {})
                return {
                    "status": "calling",
                    "call_sid": call_data.get("Sid", ""),
                    "to": to_number,
                    "from": from_number,
                    "exophone": exophone,
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("RestException", {}).get("Message", str(data)),
                }
        except Exception as e:
            logger.error("Exotel call failed: %s", e)
            return {"status": "error", "message": str(e)}

    async def send_sms(
        self,
        to_number: str,
        body: str,
        sender_id: str | None = None,
    ) -> dict:
        """Send an SMS via Exotel."""
        if not self.is_connected:
            return {"status": "not_configured", "message": "Exotel not configured"}

        exophone = sender_id or self.caller_id
        client = await self._get_client()
        try:
            response = await client.post(
                f"{self.base}/Sms/send.json",
                data={
                    "From": exophone,
                    "To": to_number,
                    "Body": body,
                },
            )
            data = response.json()
            if response.status_code == 200:
                sms_data = data.get("SMSMessage", {})
                return {
                    "status": "sent",
                    "sid": sms_data.get("Sid", ""),
                    "to": to_number,
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("RestException", {}).get("Message", str(data)),
                }
        except Exception as e:
            logger.error("Exotel SMS failed: %s", e)
            return {"status": "error", "message": str(e)}

    async def get_call_details(self, call_sid: str) -> dict:
        """Get details of a specific call."""
        if not self.is_connected:
            return {}

        client = await self._get_client()
        try:
            response = await client.get(f"{self.base}/Calls/{call_sid}.json")
            if response.status_code == 200:
                return response.json().get("Call", {})
            return {}
        except Exception as e:
            logger.error("Exotel get call failed: %s", e)
            return {}

    async def get_account_details(self) -> dict:
        """Get Exotel account info (balance, status)."""
        if not self.is_connected:
            return {"status": "not_configured"}

        client = await self._get_client()
        try:
            response = await client.get(f"{self.base}.json")
            if response.status_code == 200:
                return response.json().get("Account", {})
            return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error("Exotel account check failed: %s", e)
            return {"status": "error", "message": str(e)}

    async def list_exophones(self) -> list[dict]:
        """List all ExoPhones (virtual numbers) on the account."""
        if not self.is_connected:
            return []

        client = await self._get_client()
        try:
            response = await client.get(f"{self.base}/IncomingPhoneNumbers.json")
            if response.status_code == 200:
                numbers = response.json().get("IncomingPhoneNumbers", [])
                return [
                    {
                        "phone_number": n.get("PhoneNumber", ""),
                        "sid": n.get("Sid", ""),
                        "friendly_name": n.get("FriendlyName", ""),
                        "status": "active",
                    }
                    for n in numbers
                ]
            return []
        except Exception as e:
            logger.error("Exotel list numbers failed: %s", e)
            return []


class CallTrackingService:
    """Unified call tracking — uses Exotel (India) or Twilio (international)."""

    def __init__(self):
        self.provider = settings.CALL_PROVIDER  # "exotel" or "twilio"
        self.exotel = ExotelService()
        self.twilio_client = None

        # Initialize Twilio as backup
        if TWILIO_SDK_AVAILABLE:
            twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
            twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
            if twilio_sid and twilio_token:
                try:
                    self.twilio_client = TwilioClient(twilio_sid, twilio_token)
                except Exception:
                    pass

    @property
    def is_connected(self) -> bool:
        if self.provider == "exotel":
            return self.exotel.is_connected
        return self.twilio_client is not None

    async def provision_number(
        self,
        country_code: str = "IN",
        webhook_base_url: Optional[str] = None,
    ) -> dict:
        """Return the configured ExoPhone number info."""
        if self.provider == "exotel":
            if not self.exotel.is_connected:
                return {
                    "status": "not_configured",
                    "message": "Exotel not configured. Set EXOTEL_SID, EXOTEL_API_KEY, EXOTEL_API_TOKEN, EXOTEL_CALLER_ID on Render.",
                }
            return {
                "status": "success",
                "phone_number": self.exotel.caller_id,
                "provider": "exotel",
                "message": f"ExoPhone {self.exotel.caller_id} is active. Configure webhook in Exotel dashboard.",
                "webhook_url": f"{settings.BACKEND_BASE_URL}/api/v1/calls/exotel/incoming",
                "status_callback": f"{settings.BACKEND_BASE_URL}/api/v1/calls/exotel/status",
            }
        else:
            # Twilio fallback
            if not self.twilio_client:
                return {"status": "not_configured", "message": "Twilio not configured."}
            numbers = self.twilio_client.incoming_phone_numbers.list(limit=5)
            if numbers:
                return {
                    "status": "success",
                    "phone_number": numbers[0].phone_number,
                    "provider": "twilio",
                }
            return {"status": "no_numbers", "message": "No Twilio numbers provisioned."}

    async def list_numbers(self) -> list[dict]:
        """List all virtual numbers."""
        if self.provider == "exotel":
            return await self.exotel.list_exophones()
        elif self.twilio_client:
            try:
                numbers = self.twilio_client.incoming_phone_numbers.list(limit=50)
                return [
                    {
                        "phone_number": n.phone_number,
                        "sid": n.sid,
                        "friendly_name": n.friendly_name,
                        "status": "active",
                    }
                    for n in numbers
                ]
            except Exception:
                return []
        return []

    async def initiate_callback(
        self,
        from_number: str,
        to_number: str,
        clinic_name: str = "PatientPlex Clinic",
    ) -> dict:
        """Initiate callback to a patient."""
        if self.provider == "exotel":
            return await self.exotel.make_call(
                from_number=from_number,
                to_number=to_number,
            )
        elif self.twilio_client:
            base_url = settings.BACKEND_BASE_URL
            try:
                call = self.twilio_client.calls.create(
                    to=to_number,
                    from_=from_number,
                    twiml=(
                        f'<Response>'
                        f'<Say voice="Polly.Aditi" language="en-IN">'
                        f'Hello, this is a callback from {clinic_name}. '
                        f'Please hold while we connect you to the doctor.'
                        f'</Say>'
                        f'<Dial timeout="30" action="{base_url}/api/v1/calls/status">'
                        f'<Number>{from_number}</Number>'
                        f'</Dial>'
                        f'</Response>'
                    ),
                    status_callback=f"{base_url}/api/v1/calls/status",
                )
                return {"status": "calling", "call_sid": call.sid, "to": to_number, "from": from_number}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "not_configured", "message": "No call provider configured"}


# Module-level singleton
call_tracking_service = CallTrackingService()
