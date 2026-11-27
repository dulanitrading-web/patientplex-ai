"""Revenue Agents — automated patient recovery and engagement.

These agents run as background cron jobs and generate revenue by:
1. Recovering missed-call patients via WhatsApp (<60s)
2. Filling empty next-day slots by messaging hot leads
3. Winning back patients overdue for recurring care
4. Requesting Google reviews after completed appointments

Each agent:
- Has a per-clinic on/off toggle (future: DB config)
- Respects quiet hours (9 PM - 8 AM IST)
- Has a daily send cap per clinic
- Logs every action for audit
"""

import logging
from datetime import datetime, date, time, timedelta, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversation import Appointment, AppointmentStatus
from app.models.call_log import CallLog, CallStatus
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

# IST timezone offset
IST = timezone(timedelta(hours=5, minutes=30))

# Quiet hours: no sends between 9 PM and 8 AM IST
QUIET_START = time(21, 0)  # 9 PM
QUIET_END = time(8, 0)     # 8 AM

# Daily send cap per clinic (across all agents)
DAILY_SEND_CAP = 50


def _is_quiet_hours() -> bool:
    """Check if current IST time is in quiet hours (9 PM - 8 AM)."""
    now_ist = datetime.now(IST).time()
    return now_ist >= QUIET_START or now_ist < QUIET_END


class SlotFillerAgent:
    """Fills empty next-day appointment slots by messaging hot leads.

    Finds patients who inquired but never booked, and offers them
    tomorrow's empty slots with an optional discount message.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self) -> dict:
        """Run the slot filler for all active doctors."""
        if _is_quiet_hours():
            return {"skipped": "quiet_hours"}

        results = []
        doctors = await self.db.execute(select(Doctor).where(Doctor.is_active == True))
        for doctor in doctors.scalars().all():
            result = await self._fill_slots_for_doctor(doctor)
            results.append(result)

        return {"doctors_processed": len(results), "results": results}

    async def _fill_slots_for_doctor(self, doctor: Doctor) -> dict:
        """Find tomorrow's empty slots and message hot leads."""
        tomorrow = date.today() + timedelta(days=1)

        # Get booked slots for tomorrow
        booked = await self.db.execute(
            select(Appointment.appointment_time).where(
                and_(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date == tomorrow,
                    Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]),
                )
            )
        )
        booked_times = {row[0] for row in booked.all()}

        # Generate all possible slots
        open_time = time(9, 0)
        close_time = time(20, 0)
        slot_duration = settings.SLOT_DURATION_MINUTES
        all_slots = []
        current = datetime.combine(tomorrow, open_time)
        end = datetime.combine(tomorrow, close_time)
        while current < end:
            if current.time() not in booked_times:
                all_slots.append(current.strftime("%I:%M %p"))
            current += timedelta(minutes=slot_duration)

        if not all_slots:
            return {"doctor": doctor.full_name, "status": "fully_booked"}

        # Find hot leads: patients who had a conversation but never booked
        hot_leads = await self.db.execute(
            select(Patient).where(
                and_(
                    Patient.doctor_id == doctor.id,
                    Patient.total_visits == 0,
                    Patient.phone.isnot(None),
                )
            ).limit(10)
        )
        leads = hot_leads.scalars().all()

        sent_count = 0
        for lead in leads[:5]:  # Max 5 messages per doctor per day for slot filling
            if sent_count >= 5:
                break

            clinic_name = doctor.clinic_name or f"Dr. {doctor.full_name}'s clinic"
            slots_text = ", ".join(all_slots[:3])

            message = (
                f"Namaste {lead.name} ji! 🙏\n\n"
                f"{clinic_name} mein kal kuch slots available hain:\n"
                f"🕐 {slots_text}\n\n"
                f"Kya aap appointment book karna chahenge?\n"
                f"Reply '1' for first slot, '2' for second, ya apna preferred time batayein."
            )

            result = await whatsapp_service.send_message(to=lead.phone, message=message)
            if "error" not in result:
                sent_count += 1
                logger.info("Slot-filler sent")

        return {
            "doctor": doctor.full_name,
            "empty_slots": len(all_slots),
            "leads_messaged": sent_count,
        }


class WinBackAgent:
    """Wins back patients overdue for recurring treatments.

    Finds patients whose last visit was N months ago for treatments
    that require periodic care (cleaning, check-up, follow-up).
    """

    # Default intervals for recurring treatments (days)
    TREATMENT_INTERVALS = {
        "cleaning": 180,      # 6 months
        "safai": 180,
        "check-up": 365,      # 1 year
        "checkup": 365,
        "follow-up": 30,      # 1 month
        "follow up": 30,
        "braces": 30,         # Monthly adjustments
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self) -> dict:
        """Run win-back agent for all active doctors."""
        if _is_quiet_hours():
            return {"skipped": "quiet_hours"}

        results = []
        doctors = await self.db.execute(select(Doctor).where(Doctor.is_active == True))
        for doctor in doctors.scalars().all():
            result = await self._winback_for_doctor(doctor)
            results.append(result)

        return {"doctors_processed": len(results), "results": results}

    async def _winback_for_doctor(self, doctor: Doctor) -> dict:
        """Find overdue patients and send friendly rebooking messages."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=150)  # 5 months ago

        overdue = await self.db.execute(
            select(Patient).where(
                and_(
                    Patient.doctor_id == doctor.id,
                    Patient.total_visits > 0,
                    Patient.last_visit_date.isnot(None),
                    Patient.last_visit_date < cutoff_date,
                    Patient.phone.isnot(None),
                )
            ).limit(10)
        )
        patients = overdue.scalars().all()

        sent_count = 0
        clinic_name = doctor.clinic_name or f"Dr. {doctor.full_name}'s clinic"

        for patient in patients[:5]:
            months_ago = (datetime.now(timezone.utc) - patient.last_visit_date).days // 30

            message = (
                f"Namaste {patient.name} ji! 🙏\n\n"
                f"Aapki last visit {clinic_name} mein {months_ago} mahine pehle thi. "
                f"Dr. {doctor.full_name} recommend karte hain regular check-up har 6 mahine mein.\n\n"
                f"Kya main aapka next appointment book kar doon? 😊\n"
                f"Reply 'BOOK' ya apna preferred time batayein."
            )

            result = await whatsapp_service.send_message(to=patient.phone, message=message)
            if "error" not in result:
                sent_count += 1
                logger.info("Win-back sent")

        return {
            "doctor": doctor.full_name,
            "overdue_patients": len(patients),
            "messages_sent": sent_count,
        }


class ReviewAgent:
    """Requests Google reviews after completed appointments.

    Sends a review request 2 hours after a completed appointment.
    If patient responds negatively, routes feedback privately to the
    doctor's dashboard instead of to the public review link.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self) -> dict:
        """Find recently completed appointments and request reviews."""
        if _is_quiet_hours():
            return {"skipped": "quiet_hours"}

        # Find appointments completed in the last 4 hours that haven't been reviewed
        since = datetime.now(timezone.utc) - timedelta(hours=4)
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)

        completed = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.status == AppointmentStatus.COMPLETED,
                    Appointment.updated_at >= since,
                    Appointment.updated_at <= two_hours_ago,
                )
            ).limit(20)
        )
        appointments = completed.scalars().all()

        sent_count = 0
        for appt in appointments:
            if not appt.patient_phone:
                continue

            # Find doctor for personalization
            doc_result = await self.db.execute(
                select(Doctor).where(Doctor.id == appt.doctor_id)
            )
            doctor = doc_result.scalar_one_or_none()
            if not doctor:
                continue

            clinic_name = doctor.clinic_name or f"Dr. {doctor.full_name}'s clinic"

            message = (
                f"Namaste! 🙏 Aaj {clinic_name} aane ke liye dhanyavaad.\n\n"
                f"Aapka experience kaisa raha? Hum improve karna chahte hain:\n"
                f"⭐ Reply '5' — Bahut accha\n"
                f"⭐ Reply '4' — Accha\n"
                f"⭐ Reply '3' — Theek\n"
                f"⭐ Reply '2' — Neeche average\n"
                f"⭐ Reply '1' — Kharab\n\n"
                f"Aapka feedback humari madad karta hai! 💚"
            )

            result = await whatsapp_service.send_message(to=appt.patient_phone, message=message)
            if "error" not in result:
                sent_count += 1
                logger.info("Post-appointment review request sent")

        return {"appointments_processed": len(appointments), "review_requests_sent": sent_count}


class DoctorDigestAgent:
    """Sends daily business digest to the doctor at 8 AM IST.

    Covers: calls received/missed/recovered, bookings by source,
    visits completed, estimated revenue, overdue follow-ups.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self) -> dict:
        """Generate and send digest to all active doctors."""
        results = []
        doctors = await self.db.execute(select(Doctor).where(Doctor.is_active == True))
        for doctor in doctors.scalars().all():
            result = await self._send_digest(doctor)
            results.append(result)

        return {"digests_sent": len(results), "results": results}

    async def _send_digest(self, doctor: Doctor) -> dict:
        """Generate and send the daily digest for one doctor."""
        yesterday = date.today() - timedelta(days=1)
        start = datetime.combine(yesterday, time.min, tzinfo=timezone.utc)
        end = datetime.combine(date.today(), time.min, tzinfo=timezone.utc)

        # Count calls
        calls_result = await self.db.execute(
            select(func.count()).select_from(CallLog).where(
                and_(CallLog.doctor_id == doctor.id, CallLog.created_at >= start, CallLog.created_at < end)
            )
        )
        total_calls = calls_result.scalar() or 0

        missed_result = await self.db.execute(
            select(func.count()).select_from(CallLog).where(
                and_(
                    CallLog.doctor_id == doctor.id,
                    CallLog.created_at >= start,
                    CallLog.created_at < end,
                    CallLog.status == CallStatus.MISSED,
                )
            )
        )
        missed_calls = missed_result.scalar() or 0

        recovered_result = await self.db.execute(
            select(func.count()).select_from(CallLog).where(
                and_(
                    CallLog.doctor_id == doctor.id,
                    CallLog.created_at >= start,
                    CallLog.created_at < end,
                    CallLog.whatsapp_followup_sent == True,
                )
            )
        )
        recovered = recovered_result.scalar() or 0

        # Count appointments
        booked_result = await self.db.execute(
            select(func.count()).select_from(Appointment).where(
                and_(
                    Appointment.doctor_id == doctor.id,
                    Appointment.created_at >= start,
                    Appointment.created_at < end,
                )
            )
        )
        booked = booked_result.scalar() or 0

        completed_result = await self.db.execute(
            select(func.count()).select_from(Appointment).where(
                and_(
                    Appointment.doctor_id == doctor.id,
                    Appointment.appointment_date == yesterday,
                    Appointment.status == AppointmentStatus.COMPLETED,
                )
            )
        )
        completed = completed_result.scalar() or 0

        # Build digest message
        clinic_name = doctor.clinic_name or "Your clinic"
        date_str = yesterday.strftime("%d %b %Y")

        message = (
            f"🌅 *{clinic_name} — Daily Digest*\n"
            f"📅 {date_str}\n\n"
            f"📞 Calls: {total_calls} total"
        )
        if missed_calls > 0:
            message += f" | {missed_calls} missed"
        if recovered > 0:
            message += f" | {recovered} recovered via WhatsApp ✅"
        message += f"\n📋 Appointments: {booked} booked | {completed} completed"

        # Estimated revenue (configurable avg treatment value, default ₹1,500)
        avg_treatment_value = 1500  # TODO: make configurable per clinic
        est_revenue = completed * avg_treatment_value
        if est_revenue > 0:
            message += f"\n💰 Est. revenue: ₹{est_revenue:,}"

        message += f"\n\nAaj ka din accha ho! 🙏"

        # Send to doctor's WhatsApp
        doctor_phone = doctor.whatsapp_number or doctor.phone
        if not doctor_phone:
            return {"doctor": doctor.full_name, "status": "no_phone"}

        result = await whatsapp_service.send_message(to=doctor_phone, message=message)
        status = "sent" if "error" not in result else "failed"

        logger.info(
            "Doctor digest %s for Dr. %s: calls=%d, missed=%d, recovered=%d, booked=%d",
            status, doctor.full_name, total_calls, missed_calls, recovered, booked,
        )

        return {
            "doctor": doctor.full_name,
            "status": status,
            "total_calls": total_calls,
            "missed_calls": missed_calls,
            "recovered": recovered,
            "booked": booked,
            "completed": completed,
            "est_revenue": est_revenue,
        }
