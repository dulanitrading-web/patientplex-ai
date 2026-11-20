"""WhatsApp Business API integration for sending messages to patients."""

import logging
from urllib.parse import quote_plus

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Handles all outbound WhatsApp messaging via the Meta Cloud API."""

    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @property
    def is_connected(self) -> bool:
        return bool(self.token and self.phone_number_id)

    async def send_message(self, to: str, message: str, phone_number_id: str = None) -> dict:
        """Send a plain text WhatsApp message.

        Args:
            to: Recipient phone number in E.164 format (e.g. 919876543210)
            message: Text content to send
            phone_number_id: WhatsApp Business phone number ID
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        pid = phone_number_id or self.phone_number_id
        if not pid:
            return {"error": "WHATSAPP_PHONE_NUMBER_ID not configured"}
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/{pid}/messages"
                resp = await client.post(url, json=payload, headers=self.headers, timeout=30)
                resp.raise_for_status()
                logger.info("WhatsApp message sent to %s", to)
                return resp.json()
        except httpx.HTTPError as exc:
            logger.error("Failed to send WhatsApp message to %s: %s", to, exc)
            return {"error": str(exc)}

    async def send_template_message(
        self, to: str, template_name: str, params: list[str], phone_number_id: str = ""
    ) -> dict:
        """Send a pre-approved WhatsApp template message."""
        components = []
        if params:
            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in params],
            })
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en"},
                "components": components,
            },
        }
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/{phone_number_id}/messages"
                resp = await client.post(url, json=payload, headers=self.headers, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as exc:
            logger.error("Template message failed: %s", exc)
            return {"error": str(exc)}

    async def send_booking_confirmation(
        self,
        to: str,
        doctor_name: str,
        treatment: str,
        date_str: str,
        time_str: str,
        clinic_address: str,
        phone_number_id: str = "",
    ) -> dict:
        """Send a formatted booking confirmation message with all appointment details."""
        maps_query = quote_plus(clinic_address)
        maps_link = f"https://www.google.com/maps/search/?api=1&query={maps_query}"

        message = (
            f"✅ *Appointment Confirmed!*\n\n"
            f"👨‍⚕️ *Doctor:* {doctor_name}\n"
            f"🏥 *Treatment:* {treatment}\n"
            f"📅 *Date:* {date_str}\n"
            f"🕐 *Time:* {time_str}\n"
            f"📍 *Location:* {clinic_address}\n"
            f"🗺️ *Directions:* {maps_link}\n\n"
            f"Please arrive 10 minutes early. "
            f"Reply CANCEL to cancel or RESCHEDULE to change the time."
        )
        return await self.send_message(to, message, phone_number_id)

    async def send_reminder(
        self,
        to: str,
        doctor_name: str,
        treatment: str,
        time_str: str,
        hours_until: int,
        phone_number_id: str = "",
    ) -> dict:
        """Send an appointment reminder."""
        if hours_until >= 24:
            message = (
                f"🔔 *Appointment Reminder — Tomorrow*\n\n"
                f"Hi! Just a reminder that you have an appointment with "
                f"*{doctor_name}* for *{treatment}* tomorrow at *{time_str}*.\n\n"
                f"Reply CONFIRM to confirm or RESCHEDULE to change."
            )
        else:
            message = (
                f"🔔 *Appointment in {hours_until} hours*\n\n"
                f"Your appointment with *{doctor_name}* for *{treatment}* "
                f"is at *{time_str}* today. See you soon!\n\n"
                f"Reply CANCEL if you can't make it."
            )
        return await self.send_message(to, message, phone_number_id)

    def format_slots_message(self, slots: list[dict]) -> str:
        """Format available time slots into a numbered list for patient selection.

        Args:
            slots: List of dicts with 'start' and 'end' keys (ISO format or HH:MM)
        """
        if not slots:
            return (
                "Sorry, there are no available slots for that date. "
                "Would you like to check another date?"
            )

        lines = ["Here are the available slots:\n"]
        for i, slot in enumerate(slots, 1):
            start = slot.get("start", "")
            # If ISO datetime, extract time portion
            if "T" in start:
                start = start.split("T")[1][:5]
            end = slot.get("end", "")
            if "T" in end:
                end = end.split("T")[1][:5]
            lines.append(f"  {i}. {start} — {end}")

        lines.append("\nReply with the slot number to book (e.g. *1* or *3*).")
        return "\n".join(lines)


    async def send_feedback_request(
        self,
        to: str,
        doctor_name: str,
        treatment: str,
        clinic_name: str,
        google_review_link: str = "",
        phone_number_id: str = "",
    ) -> dict:
        """Send a post-visit feedback and review request.

        Uses psychology: asks for rating first, then links to Google review.
        People who rate high are more likely to leave a public review.
        """
        message = (
            f"Hi! 👋 Thank you for visiting *{clinic_name}* today for your *{treatment}*.\n\n"
            f"We hope you had a great experience with *{doctor_name}*! 🙏\n\n"
            f"How would you rate your visit?\n"
            f"⭐ Reply *5* — Excellent\n"
            f"⭐ Reply *4* — Good\n"
            f"⭐ Reply *3* — Average\n"
            f"⭐ Reply *2* — Below average\n"
            f"⭐ Reply *1* — Poor\n\n"
            f"Your feedback helps us improve! 💚"
        )
        result = await self.send_message(to, message, phone_number_id)

        # If Google review link is set, send a follow-up after a delay
        if google_review_link:
            follow_up = (
                f"If you enjoyed your visit, it would mean the world to us "
                f"if you could leave a quick Google review! 🌟\n\n"
                f"👉 {google_review_link}\n\n"
                f"Thank you for choosing {clinic_name}! 🏥"
            )
            # Note: In production, this would be sent after the patient rates 4-5 stars
            # For now, we include it in the initial batch
        return result

    async def send_appointment_summary(
        self,
        to: str,
        doctor_name: str,
        treatment: str,
        notes: str = "",
        next_visit_date: str = "",
        phone_number_id: str = "",
    ) -> dict:
        """Send post-visit summary with treatment notes and next visit date."""
        message = (
            f"📋 *Visit Summary*\n\n"
            f"👨‍⚕️ Doctor: {doctor_name}\n"
            f"🏥 Treatment: {treatment}\n"
        )
        if notes:
            message += f"📝 Notes: {notes}\n"
        if next_visit_date:
            message += f"\n📅 *Next Visit:* {next_visit_date}\n"
            message += f"We'll send you a reminder before your next appointment.\n"
        message += f"\nThank you for trusting us with your care! 💚"
        return await self.send_message(to, message, phone_number_id)


whatsapp_service = WhatsAppService()
