"""
PatientPlex EHR, Calendar & Revenue Integration

Connects with clinic management systems to track:
- Patient appointments (booked, attended, no-show)
- Treatment revenue
- Cost per appointment
- Patient lifetime value
- Calendar sync for availability
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


@dataclass
class Appointment:
    id: str
    clinic_id: str
    patient_id: str
    doctor_id: str
    treatment: str
    scheduled_at: str
    status: AppointmentStatus
    source_platform: str = ""  # google_ads, meta, whatsapp, organic
    source_campaign_id: str = ""
    revenue_inr: float = 0.0
    cost_of_acquisition_inr: float = 0.0
    notes: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


@dataclass
class DailySlot:
    time: str
    duration_minutes: int = 30
    is_available: bool = True
    appointment_id: Optional[str] = None


class EHRIntegration:
    """Manages clinic calendar, appointments, and revenue tracking."""

    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self.clinic_slots: Dict[str, Dict[str, List[DailySlot]]] = {}
        self.treatments_catalog: Dict[str, Dict] = {}

    # === APPOINTMENT MANAGEMENT ===

    def book_appointment(self, appointment: Appointment) -> Dict:
        """Book a new appointment."""
        self.appointments[appointment.id] = appointment

        # Mark slot as taken
        date_key = appointment.scheduled_at[:10]
        if appointment.clinic_id in self.clinic_slots:
            if date_key in self.clinic_slots[appointment.clinic_id]:
                for slot in self.clinic_slots[appointment.clinic_id][date_key]:
                    if (
                        slot.time == appointment.scheduled_at[11:16]
                        and slot.is_available
                    ):
                        slot.is_available = False
                        slot.appointment_id = appointment.id
                        break

        return {
            "status": "booked",
            "appointment_id": appointment.id,
            "patient_id": appointment.patient_id,
            "scheduled_at": appointment.scheduled_at,
            "treatment": appointment.treatment,
        }

    def update_appointment_status(
        self,
        appointment_id: str,
        status: AppointmentStatus,
        revenue_inr: float = 0,
    ) -> Dict:
        """Update appointment status (check-in, complete, no-show)."""
        apt = self.appointments.get(appointment_id)
        if not apt:
            return {"status": "error", "message": "Appointment not found"}

        apt.status = status
        if revenue_inr > 0:
            apt.revenue_inr = revenue_inr

        return {
            "status": "updated",
            "appointment_id": appointment_id,
            "new_status": status.value,
            "revenue_inr": apt.revenue_inr,
        }

    def get_appointment(self, appointment_id: str) -> Optional[Dict]:
        """Get a single appointment by ID."""
        apt = self.appointments.get(appointment_id)
        if not apt:
            return None
        return {
            "id": apt.id,
            "clinic_id": apt.clinic_id,
            "patient_id": apt.patient_id,
            "doctor_id": apt.doctor_id,
            "treatment": apt.treatment,
            "scheduled_at": apt.scheduled_at,
            "status": apt.status.value,
            "source_platform": apt.source_platform,
            "revenue_inr": apt.revenue_inr,
            "cost_of_acquisition_inr": apt.cost_of_acquisition_inr,
        }

    # === CALENDAR / AVAILABILITY ===

    def set_clinic_schedule(
        self,
        clinic_id: str,
        doctor_id: str,
        date_str: str,
        slots: List[Dict],
    ) -> Dict:
        """Set available slots for a clinic on a given date."""
        if clinic_id not in self.clinic_slots:
            self.clinic_slots[clinic_id] = {}

        daily_slots = []
        for s in slots:
            daily_slots.append(
                DailySlot(
                    time=s["time"],
                    duration_minutes=s.get("duration", 30),
                    is_available=True,
                )
            )

        self.clinic_slots[clinic_id][date_str] = daily_slots
        return {
            "status": "set",
            "clinic_id": clinic_id,
            "date": date_str,
            "slots": len(daily_slots),
        }

    def get_available_slots(
        self, clinic_id: str, date_str: str
    ) -> List[Dict]:
        """Get available appointment slots."""
        if (
            clinic_id not in self.clinic_slots
            or date_str not in self.clinic_slots[clinic_id]
        ):
            return []

        return [
            {
                "time": s.time,
                "duration": s.duration_minutes,
                "available": s.is_available,
            }
            for s in self.clinic_slots[clinic_id][date_str]
            if s.is_available
        ]

    # === REVENUE & BUSINESS METRICS ===

    def get_revenue_metrics(
        self,
        clinic_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """Get revenue and business metrics for a clinic."""
        clinic_appointments = [
            a for a in self.appointments.values() if a.clinic_id == clinic_id
        ]

        if start_date:
            clinic_appointments = [
                a for a in clinic_appointments if a.scheduled_at >= start_date
            ]
        if end_date:
            clinic_appointments = [
                a for a in clinic_appointments if a.scheduled_at <= end_date
            ]

        total = len(clinic_appointments)
        completed = [
            a
            for a in clinic_appointments
            if a.status == AppointmentStatus.COMPLETED
        ]
        no_shows = [
            a
            for a in clinic_appointments
            if a.status == AppointmentStatus.NO_SHOW
        ]
        cancelled = [
            a
            for a in clinic_appointments
            if a.status == AppointmentStatus.CANCELLED
        ]

        total_revenue = sum(a.revenue_inr for a in completed)
        total_acquisition_cost = sum(
            a.cost_of_acquisition_inr for a in clinic_appointments
        )

        # By source
        by_source: Dict[str, Dict] = {}
        for a in clinic_appointments:
            src = a.source_platform or "unknown"
            if src not in by_source:
                by_source[src] = {
                    "count": 0,
                    "revenue": 0.0,
                    "cost": 0.0,
                    "completed": 0,
                    "no_shows": 0,
                }
            by_source[src]["count"] += 1
            by_source[src]["cost"] += a.cost_of_acquisition_inr
            if a.status == AppointmentStatus.COMPLETED:
                by_source[src]["completed"] += 1
                by_source[src]["revenue"] += a.revenue_inr
            if a.status == AppointmentStatus.NO_SHOW:
                by_source[src]["no_shows"] += 1

        for src, data in by_source.items():
            data["roas"] = round(
                data["revenue"] / max(data["cost"], 1), 2
            )
            data["cost_per_booking"] = round(
                data["cost"] / max(data["count"], 1), 2
            )
            data["cost_per_completed"] = round(
                data["cost"] / max(data["completed"], 1), 2
            )
            data["no_show_rate"] = round(
                data["no_shows"] / max(data["count"], 1) * 100, 1
            )

        # By treatment
        by_treatment: Dict[str, Dict] = {}
        for a in completed:
            t = a.treatment or "Other"
            if t not in by_treatment:
                by_treatment[t] = {"count": 0, "revenue": 0.0}
            by_treatment[t]["count"] += 1
            by_treatment[t]["revenue"] += a.revenue_inr

        return {
            "period": {"start": start_date, "end": end_date},
            "total_appointments": total,
            "completed": len(completed),
            "no_shows": len(no_shows),
            "cancelled": len(cancelled),
            "no_show_rate": round(
                len(no_shows) / max(total, 1) * 100, 1
            ),
            "show_rate": round(
                len(completed) / max(total, 1) * 100, 1
            ),
            "total_revenue_inr": round(total_revenue, 2),
            "avg_revenue_per_appointment_inr": round(
                total_revenue / max(len(completed), 1), 2
            ),
            "total_acquisition_cost_inr": round(total_acquisition_cost, 2),
            "cost_per_appointment_inr": round(
                total_acquisition_cost / max(total, 1), 2
            ),
            "cost_per_completed_inr": round(
                total_acquisition_cost / max(len(completed), 1), 2
            ),
            "roas": round(
                total_revenue / max(total_acquisition_cost, 1), 2
            ),
            "profit_inr": round(
                total_revenue - total_acquisition_cost, 2
            ),
            "by_source": by_source,
            "by_treatment": by_treatment,
        }

    def get_cost_per_dollar_booked(self, clinic_id: str) -> Dict:
        """Calculate the cost to generate each rupee of appointment revenue."""
        clinic_apts = [
            a
            for a in self.appointments.values()
            if a.clinic_id == clinic_id
            and a.status == AppointmentStatus.COMPLETED
        ]

        total_revenue = sum(a.revenue_inr for a in clinic_apts)
        total_cost = sum(a.cost_of_acquisition_inr for a in clinic_apts)

        if total_revenue == 0:
            return {
                "cost_per_rupee_revenue": 0,
                "message": "No completed appointments with revenue",
            }

        return {
            "cost_per_rupee_revenue": round(total_cost / total_revenue, 4),
            "for_every_100_rupees_revenue_you_spend": round(
                (total_cost / total_revenue) * 100, 2
            ),
            "total_revenue": round(total_revenue, 2),
            "total_marketing_cost": round(total_cost, 2),
            "roi_multiple": round(
                total_revenue / max(total_cost, 1), 2
            ),
            "completed_appointments": len(clinic_apts),
        }
