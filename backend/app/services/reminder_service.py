"""Automated appointment reminder service.

Checks for upcoming appointments and sends WhatsApp reminders at 24h and 2h.
Also marks no-shows for appointments past their time.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class ReminderService:
    """Handles automated appointment reminders and no-show marking."""

    async def check_and_send_reminders(self, db: AsyncSession) -> dict:
        """Check all upcoming appointments and send due reminders.

        Returns a summary of reminders sent.
        """
        now = datetime.now(timezone.utc)
        summary = {"24h_sent": 0, "2h_sent": 0, "errors": 0}

        # 24-hour reminders: appointments between 23-25 hours from now
        window_24h_start = now + timedelta(hours=23)
        window_24h_end = now + timedelta(hours=25)
        await self._send_reminders_in_window(
            db, window_24h_start, window_24h_end,
            reminder_type="24h", summary=summary,
        )

        # 2-hour reminders: appointments between 1.5-2.5 hours from now
        window_2h_start = now + timedelta(hours=1, minutes=30)
        window_2h_end = now + timedelta(hours=2, minutes=30)
        await self._send_reminders_in_window(
            db, window_2h_start, window_2h_end,
            reminder_type="2h", summary=summary,
        )

        await db.commit()
        logger.info("Reminder check complete: %s", summary)
        return summary

    async def _send_reminders_in_window(
        self,
        db: AsyncSession,
        window_start: datetime,
        window_end: datetime,
        reminder_type: str,
        summary: dict,
    ) -> None:
        """Send reminders for appointments within a time window."""
        is_24h = reminder_type == "24h"
        sent_field = "reminder_24h_sent" if is_24h else "reminder_2h_sent"

        # Query appointments in window that haven't been reminded yet
        result = await db.execute(
            select(Appointment, Doctor)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .where(
                and_(
                    Appointment.status.in_([
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.REMINDED,
                    ]),
                    getattr(Appointment, sent_field) == False,
                )
            )
        )
        rows = result.all()

        for appointment, doctor in rows:
            # Combine date+time to check if in window
            appt_dt = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time,
                tzinfo=timezone.utc,
            )
            if not (window_start <= appt_dt <= window_end):
                continue

            hours_until = 24 if is_24h else 2
            try:
                await whatsapp_service.send_reminder(
                    to=appointment.patient_phone,
                    doctor_name=doctor.full_name,
                    treatment=appointment.treatment,
                    time_str=appointment.appointment_time.strftime("%I:%M %p"),
                    hours_until=hours_until,
                )
                if is_24h:
                    appointment.reminder_24h_sent = True
                else:
                    appointment.reminder_2h_sent = True
                appointment.status = AppointmentStatus.REMINDED
                summary[f"{reminder_type}_sent"] += 1
                logger.info("Sent %s reminder for appointment %s", reminder_type, appointment.id)
            except Exception as exc:
                logger.error("Failed to send %s reminder for %s: %s", reminder_type, appointment.id, exc)
                summary["errors"] += 1

    async def mark_no_shows(self, db: AsyncSession) -> int:
        """Mark appointments as NO_SHOW if their time has passed (1h grace period).

        Returns the count of newly marked no-shows.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=1)

        result = await db.execute(
            select(Appointment).where(
                and_(
                    Appointment.status.in_([
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.REMINDED,
                    ]),
                )
            )
        )
        appointments = result.scalars().all()
        count = 0

        for appt in appointments:
            appt_dt = datetime.combine(appt.appointment_date, appt.appointment_time, tzinfo=timezone.utc)
            if appt_dt < cutoff:
                appt.status = AppointmentStatus.NO_SHOW
                count += 1

        if count:
            await db.commit()
            logger.info("Marked %d appointments as NO_SHOW", count)

        return count


reminder_service = ReminderService()
