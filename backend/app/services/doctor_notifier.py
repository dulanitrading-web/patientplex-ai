"""Doctor notification service — alerts the doctor about new bookings, missed calls, etc.

Sends notifications via:
1. WhatsApp (primary) — doctor gets a formatted booking card
2. SMS (fallback) — if WhatsApp fails
3. In-app (dashboard) — always recorded for the doctor to review
"""

import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus

from app.models.conversation import Appointment
from app.models.doctor import Doctor
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class DoctorNotifier:
    """Sends real-time notifications to doctors about patient activity."""

    async def notify_new_booking(
        self,
        doctor: Doctor,
        appointment: Appointment,
    ) -> dict:
        """Notify the doctor when a new appointment is booked.

        Sends a formatted WhatsApp message with:
        - Patient name and phone
        - Treatment
        - Date and time
        - How the patient found them (source)
        """
        date_str = appointment.appointment_date.strftime("%A, %d %b %Y")
        time_str = appointment.appointment_time.strftime("%I:%M %p")

        message = (
            f"🔔 *New Appointment Booked!*\n\n"
            f"👤 *Patient:* {appointment.patient_name}\n"
            f"📞 *Phone:* {appointment.patient_phone}\n"
            f"🏥 *Treatment:* {appointment.treatment}\n"
            f"📅 *Date:* {date_str}\n"
            f"🕐 *Time:* {time_str}\n"
            f"⏱️ *Duration:* {appointment.duration_minutes} minutes\n"
            f"📍 *Source:* {'Missed call → WhatsApp' if hasattr(appointment, 'source') else 'WhatsApp'}\n\n"
            f"This appointment has been added to your Google Calendar. "
            f"The patient has received a WhatsApp confirmation."
        )

        doctor_phone = doctor.whatsapp_number or doctor.phone
        if not doctor_phone:
            logger.warning("No phone number for doctor %s", doctor.id)
            return {"status": "no_phone"}

        result = await whatsapp_service.send_message(
            to=doctor_phone.replace("+", ""),
            message=message,
        )

        if "error" in result:
            logger.error("Doctor notification failed: %s", result)
            return {"status": "failed", "error": result}

        logger.info("Doctor %s notified about new booking", doctor.full_name)
        return {"status": "sent"}

    async def notify_missed_call(
        self,
        doctor: Doctor,
        caller_phone: str,
        whatsapp_sent: bool = True,
    ) -> dict:
        """Notify doctor about a missed call that was recovered via WhatsApp."""
        message = (
            f"📞 *Missed Call Alert*\n\n"
            f"A patient called from *{caller_phone}* but couldn't reach you.\n"
        )
        if whatsapp_sent:
            message += (
                f"\n✅ Our AI assistant has already reached out to them on "
                f"WhatsApp and is helping them book an appointment. "
                f"You'll be notified when they book."
            )
        else:
            message += (
                f"\n⚠️ We couldn't reach them on WhatsApp. "
                f"You may want to call them back."
            )

        doctor_phone = doctor.whatsapp_number or doctor.phone
        if not doctor_phone:
            return {"status": "no_phone"}

        return await whatsapp_service.send_message(
            to=doctor_phone.replace("+", ""),
            message=message,
        )

    async def notify_cancellation(
        self,
        doctor: Doctor,
        appointment: Appointment,
    ) -> dict:
        """Notify doctor when a patient cancels."""
        date_str = appointment.appointment_date.strftime("%d %b")
        time_str = appointment.appointment_time.strftime("%I:%M %p")

        message = (
            f"❌ *Appointment Cancelled*\n\n"
            f"*{appointment.patient_name}* has cancelled their "
            f"*{appointment.treatment}* appointment on {date_str} at {time_str}.\n\n"
            f"This slot is now open on your calendar."
        )

        doctor_phone = doctor.whatsapp_number or doctor.phone
        if not doctor_phone:
            return {"status": "no_phone"}

        return await whatsapp_service.send_message(
            to=doctor_phone.replace("+", ""),
            message=message,
        )

    async def send_daily_summary(
        self,
        doctor: Doctor,
        total_bookings: int,
        total_calls: int,
        missed_calls: int,
        missed_recovered: int,
        tomorrow_appointments: list[dict],
    ) -> dict:
        """Send a daily summary to the doctor every evening."""
        appt_lines = ""
        for appt in tomorrow_appointments[:5]:
            appt_lines += f"  • {appt['time']} — {appt['patient_name']} ({appt['treatment']})\n"

        if not appt_lines:
            appt_lines = "  No appointments tomorrow.\n"

        message = (
            f"📊 *Daily Summary — {datetime.now(timezone.utc).strftime('%d %b %Y')}*\n\n"
            f"📞 Calls: {total_calls} ({missed_calls} missed → {missed_recovered} recovered)\n"
            f"📅 New bookings: {total_bookings}\n\n"
            f"*Tomorrow's Schedule:*\n{appt_lines}\n"
            f"Open your PatientPlex AI dashboard for full details."
        )

        doctor_phone = doctor.whatsapp_number or doctor.phone
        if not doctor_phone:
            return {"status": "no_phone"}

        return await whatsapp_service.send_message(
            to=doctor_phone.replace("+", ""),
            message=message,
        )
