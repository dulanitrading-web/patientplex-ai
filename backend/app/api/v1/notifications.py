"""Notifications API — real-time alerts for doctors.

Generates notifications from actual clinic events:
- New appointment booked
- Appointment status changes
- Campaign milestones (spend thresholds, impression milestones)
- System alerts (integration disconnected, budget depleted)
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.db.session import get_db
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
async def get_notifications(
    limit: int = Query(10, le=50),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get the doctor's recent notifications derived from real events."""
    notifications = []
    now = datetime.now(timezone.utc)
    today = date.today()

    # 1. Recent appointments (booked in last 24h)
    yesterday = now - timedelta(hours=24)
    recent_appts = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.created_at >= yesterday,
            )
        ).order_by(Appointment.created_at.desc()).limit(5)
    )
    for a in recent_appts.scalars().all():
        age = _time_ago(a.created_at, now)
        notifications.append({
            "id": f"appt-{a.id}",
            "type": "new_booking",
            "message": f"New appointment: {a.patient_name} — {a.treatment} on {a.appointment_date.strftime('%d %b')} at {a.appointment_time.strftime('%I:%M %p')}",
            "timestamp": age,
            "read": (now - a.created_at).total_seconds() > 3600,  # Read if >1h old
        })

    # 2. Today's upcoming appointments
    upcoming = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
                Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.REMINDED]),
            )
        ).order_by(Appointment.appointment_time.asc())
    )
    upcoming_list = upcoming.scalars().all()
    if upcoming_list:
        notifications.append({
            "id": f"today-{today.isoformat()}",
            "type": "system",
            "message": f"You have {len(upcoming_list)} appointment{'s' if len(upcoming_list) > 1 else ''} today. Next: {upcoming_list[0].patient_name} at {upcoming_list[0].appointment_time.strftime('%I:%M %p')}",
            "timestamp": "Today",
            "read": False,
        })

    # 3. No-shows from yesterday
    yesterday_date = today - timedelta(days=1)
    no_shows = await db.execute(
        select(func.count()).select_from(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == yesterday_date,
                Appointment.status == AppointmentStatus.NO_SHOW,
            )
        )
    )
    no_show_count = no_shows.scalar() or 0
    if no_show_count > 0:
        notifications.append({
            "id": f"noshow-{yesterday_date.isoformat()}",
            "type": "missed_call",
            "message": f"{no_show_count} no-show{'s' if no_show_count > 1 else ''} yesterday. Consider sending follow-up messages.",
            "timestamp": "Yesterday",
            "read": True,
        })

    # 4. Integration status alerts
    if not doctor.google_ads_connected:
        notifications.append({
            "id": "int-gads",
            "type": "system",
            "message": "Google Ads is not connected. Connect it in Settings to start running campaigns.",
            "timestamp": "",
            "read": True,
        })
    if not doctor.whatsapp_verified:
        notifications.append({
            "id": "int-wa",
            "type": "system",
            "message": "WhatsApp AI receptionist is not active. Set it up in Settings to auto-respond to patients.",
            "timestamp": "",
            "read": True,
        })

    # 5. This month's milestone
    month_start = today.replace(day=1)
    month_appts = await db.execute(
        select(func.count()).select_from(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= month_start,
            )
        )
    )
    month_count = month_appts.scalar() or 0
    if month_count > 0 and month_count % 10 == 0:
        notifications.append({
            "id": f"milestone-{month_count}",
            "type": "campaign_update",
            "message": f"Milestone: {month_count} appointments booked this month!",
            "timestamp": "This month",
            "read": False,
        })

    # Sort: unread first, then by recency
    notifications.sort(key=lambda n: (n["read"], n["timestamp"] != "Today"))

    return {
        "notifications": notifications[:limit],
        "unread_count": sum(1 for n in notifications if not n["read"]),
        "total": len(notifications),
    }


def _time_ago(dt: datetime, now: datetime) -> str:
    """Human-readable time ago string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins} min ago"
    if seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    days = int(seconds / 86400)
    if days == 1:
        return "Yesterday"
    return f"{days} days ago"
