"""Call Tracking Number Service — provisions Twilio virtual numbers for clinics.

Each clinic gets a unique Twilio virtual number that:
1. Is used in Google Ads call extensions (Google shows this number)
2. Captures the REAL caller's phone number (Google blurs it otherwise)
3. Forwards calls to the doctor's actual phone
4. Records calls for quality assurance
5. Detects missed calls → triggers WhatsApp AI follow-up
6. Enables callback when a call is missed

This solves the "Google blurs the number" problem:
- Without PatientPlex: Google Ads shows a forwarding number, doctor never sees real patient number
- With PatientPlex: Twilio captures real number → stored in call_logs → clinic can call back

Flow:
  Patient calls Twilio number (from Google Ad) →
  Twilio sends webhook to PatientPlex →
  PatientPlex logs caller's REAL number →
  Forwards call to doctor's phone →
  If missed → WhatsApp follow-up with patient's real number →
  Doctor can see all caller numbers in dashboard + call back
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Conditionally import Twilio
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_SDK_AVAILABLE = True
except ImportError:
    TWILIO_SDK_AVAILABLE = False
    TwilioClient = None
    logger.warning("twilio SDK not installed — pip install twilio")


class CallTrackingService:
    """Provisions and manages Twilio virtual numbers for clinic call tracking."""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.client = None

        if TWILIO_SDK_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.client = TwilioClient(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized for call tracking")
            except Exception as e:
                logger.error("Failed to initialize Twilio client: %s", e)

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    async def provision_number(
        self,
        country_code: str = "IN",
        area_code: Optional[str] = None,
        webhook_base_url: Optional[str] = None,
    ) -> dict:
        """Provision a new Twilio virtual number for a clinic.

        For India:
        - Twilio offers Indian virtual numbers (requires regulatory bundle)
        - Alternative: Use a US/UK number with forwarding
        - Best option: Buy Indian DID number through Twilio

        Args:
            country_code: ISO country code (IN for India)
            area_code: Optional local area code for the number
            webhook_base_url: Base URL for Twilio webhooks (e.g. https://api.patientplex.ai)

        Returns:
            dict with phone_number, sid, and capabilities
        """
        if not self.is_connected:
            return {
                "status": "demo_mode",
                "message": "Twilio not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.",
                "phone_number": "+91XXXXXXXXXX",
                "sid": "demo",
            }

        base_url = webhook_base_url or os.getenv(
            "BACKEND_URL", "https://patientplex-ai-g7ce.onrender.com"
        )

        try:
            # Search for available numbers
            search_params = {"country": country_code, "voice_enabled": True}
            if area_code:
                search_params["area_code"] = area_code

            # Try Indian numbers first
            if country_code == "IN":
                try:
                    available = self.client.available_phone_numbers("IN").local.list(
                        voice_enabled=True, limit=5
                    )
                except Exception:
                    available = []
                if not available:
                    # Fallback to Indian mobile numbers
                    try:
                        available = self.client.available_phone_numbers("IN").mobile.list(
                            voice_enabled=True, limit=5
                        )
                    except Exception:
                        available = []
                if not available:
                    # India numbers require regulatory bundle approval in Twilio.
                    # Fall back to a US number for call tracking — it still works for
                    # Google Ads call extensions (call forwarding) globally.
                    logger.warning(
                        "No Indian numbers available on this Twilio account "
                        "(regulatory bundle required). Provisioning a US number instead."
                    )
                    try:
                        available = self.client.available_phone_numbers("US").local.list(
                            voice_enabled=True, limit=5
                        )
                    except Exception:
                        available = []

            if not available:
                return {
                    "status": "no_numbers",
                    "message": (
                        "No phone numbers available. Indian DID numbers require a "
                        "regulatory bundle approval at twilio.com/console/phone-numbers. "
                        "Contact support@patientplex.ai to provision a tracking number manually."
                    ),
                }

            # Buy the first available number
            number = self.client.incoming_phone_numbers.create(
                phone_number=available[0].phone_number,
                voice_url=f"{base_url}/api/v1/calls/incoming",
                voice_method="POST",
                status_callback=f"{base_url}/api/v1/calls/status",
                status_callback_method="POST",
                voice_fallback_url=f"{base_url}/api/v1/calls/incoming",
                friendly_name="PatientPlex Call Tracking",
            )

            return {
                "status": "provisioned",
                "phone_number": number.phone_number,
                "sid": number.sid,
                "friendly_name": number.friendly_name,
                "capabilities": {
                    "voice": number.capabilities.get("voice", False),
                    "sms": number.capabilities.get("sms", False),
                },
                "webhook_url": f"{base_url}/api/v1/calls/incoming",
            }

        except Exception as e:
            logger.error("Failed to provision Twilio number: %s", e)
            return {"status": "error", "message": str(e)}

    async def list_numbers(self) -> list[dict]:
        """List all Twilio numbers in the account."""
        if not self.is_connected:
            return []

        try:
            numbers = self.client.incoming_phone_numbers.list(limit=50)
            return [
                {
                    "phone_number": n.phone_number,
                    "sid": n.sid,
                    "friendly_name": n.friendly_name,
                    "voice_url": n.voice_url,
                    "status": "active",
                }
                for n in numbers
            ]
        except Exception as e:
            logger.error("Failed to list Twilio numbers: %s", e)
            return []

    async def initiate_callback(
        self,
        from_number: str,
        to_number: str,
        clinic_name: str = "PatientPlex Clinic",
    ) -> dict:
        """Initiate an outbound callback to a patient who called earlier.

        This uses Twilio to call the patient back from the clinic's
        virtual number, connecting them to the doctor.

        Args:
            from_number: Clinic's Twilio virtual number
            to_number: Patient's phone number (from call logs)
            clinic_name: For the voice greeting
        """
        if not self.is_connected:
            return {
                "status": "demo_mode",
                "message": "Twilio not configured",
            }

        base_url = os.getenv(
            "BACKEND_URL", "https://patientplex-ai-g7ce.onrender.com"
        )

        try:
            call = self.client.calls.create(
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
            return {
                "status": "calling",
                "call_sid": call.sid,
                "to": to_number,
                "from": from_number,
            }
        except Exception as e:
            logger.error("Callback failed: %s", e)
            return {"status": "error", "message": str(e)}


# Module-level singleton
call_tracking_service = CallTrackingService()
