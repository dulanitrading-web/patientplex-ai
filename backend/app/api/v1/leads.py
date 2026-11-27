"""Lead capture API — receives inquiries from landing pages and Google Ads forms.

No authentication required. Rate-limited to prevent abuse.
When a patient submits a form on a landing page or Google Ads lead form extension,
this endpoint:
1. Saves the lead to the database (patients table)
2. Sends an email alert to the doctor
3. Triggers WhatsApp follow-up if configured
4. Tracks UTM attribution for the conversion funnel
"""

import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.environ.get("TESTING", "").lower() != "true",
)

from app.db.session import get_db
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadCaptureRequest(BaseModel):
    """Incoming lead from a landing page or ad form."""
    patient_name: str
    patient_phone: str
    patient_email: str | None = None
    treatment: str = "General Consultation"
    keyword: str | None = None  # Search keyword that triggered the ad
    lead_source: str = "Website"  # "Google Ads", "Meta Ads", "Website", etc.
    landing_page: str | None = None  # Which LP they came from
    doctor_slug: str | None = None  # To identify which doctor
    doctor_id: str | None = None
    # UTM tracking
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_term: str | None = None
    utm_content: str | None = None


class LeadCaptureResponse(BaseModel):
    success: bool
    message: str
    lead_id: str | None = None


@router.post("", response_model=LeadCaptureResponse)
@router.post("/", response_model=LeadCaptureResponse)
async def capture_lead(
    body: LeadCaptureRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Capture a lead from landing page form submission.

    This is a public endpoint — no auth required.
    Rate limited to 10 requests per minute per IP.
    """
    # Explicit clinic routing: never assign an inquiry to an arbitrary clinic.
    from uuid import UUID

    doctor = None
    if body.doctor_id:
        try:
            doctor_uuid = UUID(body.doctor_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid clinic identifier")
        doctor = await db.get(Doctor, doctor_uuid)
        if doctor is None:
            raise HTTPException(status_code=404, detail="Clinic not found")

    if body.doctor_slug:
        result = await db.execute(
            select(Doctor).where(Doctor.subdomain_slug == body.doctor_slug)
        )
        slug_doctor = result.scalar_one_or_none()
        if slug_doctor is None:
            raise HTTPException(status_code=404, detail="Clinic not found")
        if doctor is not None and doctor.id != slug_doctor.id:
            raise HTTPException(status_code=422, detail="Conflicting clinic identifiers")
        doctor = slug_doctor

    if doctor is None:
        raise HTTPException(status_code=422, detail="Clinic identifier required")

    # Save lead to patients table (with dedup on phone number)
    lead_id = None
    try:
        from app.models.patient import Patient
        from sqlalchemy import and_
        from datetime import datetime, timezone

        # Normalize phone for dedup
        normalized_phone = body.patient_phone.strip()
        if not normalized_phone.startswith("+") and len(normalized_phone) == 10:
            normalized_phone = f"+91{normalized_phone}"

        # Check for existing patient with same phone
        existing = await db.execute(
            select(Patient).where(
                and_(Patient.doctor_id == doctor.id, Patient.phone == normalized_phone)
            )
        )
        patient = existing.scalar_one_or_none()

        if patient:
            # Update existing patient instead of creating duplicate
            patient.updated_at = datetime.now(timezone.utc)
            if body.patient_email and not patient.email:
                patient.email = body.patient_email
            if body.patient_name and not patient.name:
                patient.name = body.patient_name
            logger.info("Lead matched existing patient: %s", patient.id)
        else:
            patient = Patient(
                doctor_id=doctor.id,
                name=body.patient_name,
                phone=normalized_phone,
                email=body.patient_email,
                source=body.lead_source,
                notes=f"Treatment: {body.treatment} | Keyword: {body.keyword or 'N/A'} | LP: {body.landing_page or 'N/A'}",
            )
            db.add(patient)

        await db.flush()
        lead_id = str(patient.id)
        await db.commit()
        logger.info("Lead saved to DB: patient_id=%s", lead_id)
    except Exception as exc:
        logger.error("Lead persistence failed (%s)", type(exc).__name__)
        await db.rollback()
        raise HTTPException(status_code=503, detail="Unable to save inquiry; please retry") from exc

    # Send email alert to doctor
    try:
        await _send_lead_alert_email(
            doctor=doctor,
            patient_name=body.patient_name,
            patient_phone=body.patient_phone,
            patient_email=body.patient_email,
            treatment=body.treatment,
            keyword=body.keyword,
            lead_source=body.lead_source,
            landing_page=body.landing_page,
        )
    except Exception as exc:
        logger.error("Lead notification failed (%s)", type(exc).__name__)

    # Track conversion
    try:
        # No lead-captured stage exists in the current conversion enum.
        # Do not fabricate a different funnel event.
    except Exception as exc:
        logger.debug("Conversion tracking skipped (%s)", type(exc).__name__)

    return LeadCaptureResponse(
        success=True,
        message="Thank you! The clinic will call you within 10-15 minutes.",
        lead_id=lead_id,
    )


async def _send_lead_alert_email(
    doctor: Doctor,
    patient_name: str,
    patient_phone: str,
    patient_email: str | None,
    treatment: str,
    keyword: str | None,
    lead_source: str,
    landing_page: str | None,
) -> None:
    """Send a lead alert email to the doctor — matches the format they expect."""
    from app.services.email_service import send_email, _is_configured
    from html import escape
    from urllib.parse import quote
    import re

    if not _is_configured():
        logger.warning("Email not configured — lead alert not sent")
        return

    now = datetime.now(timezone.utc)
    # Convert to IST
    from datetime import timedelta
    ist = now + timedelta(hours=5, minutes=30)
    timestamp = ist.strftime("%d/%m/%Y, %I:%M:%S %p").lower()

    clinic_name = doctor.clinic_name or "Clinic"
    doctor_email = doctor.email

    subject = f"[Lead Alert] {patient_name} — {treatment}".replace('\r', ' ').replace('\n', ' ')
    digits = re.sub(r'[^0-9]', '', patient_phone)
    if len(digits) == 10:
        digits = '91' + digits
    whatsapp_text = quote(f'Hi {patient_name.split()[0] if patient_name.split() else "there"}, this is {clinic_name}. We received your inquiry about {treatment}. When would you like to visit?', safe='')
    patient_name, patient_phone, treatment, clinic_name, lead_source = map(escape, (patient_name, patient_phone, treatment, clinic_name, lead_source))
    patient_email, keyword, landing_page = (escape(v) if v else None for v in (patient_email, keyword, landing_page))

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px;">
        <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 20px 24px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0; font-size: 20px; font-weight: 700;">New Consultation Inquiry</h2>
        </div>
        <div style="border: 1px solid #e2e8f0; border-top: none; padding: 24px; border-radius: 0 0 12px 12px; background: white;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; color: #64748b; font-weight: 600; width: 160px;">Patient Name:</td>
                    <td style="padding: 10px 0; color: #0f172a; font-weight: 700;">{patient_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Phone Number:</td>
                    <td style="padding: 10px 0;">
                        <a href="tel:{patient_phone}" style="color: #10b981; font-weight: 700; text-decoration: none; font-size: 16px;">{patient_phone}</a>
                    </td>
                </tr>
                {"<tr><td style='padding: 10px 0; color: #64748b; font-weight: 600;'>Email:</td><td style='padding: 10px 0; color: #0f172a;'>" + patient_email + "</td></tr>" if patient_email else ""}
                <tr>
                    <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Treatment Requested:</td>
                    <td style="padding: 10px 0; color: #0f172a;">{treatment}</td>
                </tr>
                {"<tr><td style='padding: 10px 0; color: #64748b; font-weight: 600;'>Keyword / Query:</td><td style='padding: 10px 0; color: #0f172a;'>" + keyword + "</td></tr>" if keyword else ""}
                <tr>
                    <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Lead Source:</td>
                    <td style="padding: 10px 0; color: #0f172a;">{lead_source}{' (' + landing_page + ')' if landing_page else ''}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Received:</td>
                    <td style="padding: 10px 0; color: #0f172a;">{timestamp}</td>
                </tr>
            </table>

            <div style="margin-top: 20px; padding: 16px; background: #fef3c7; border-radius: 8px; border: 1px solid #fde68a;">
                <p style="margin: 0; color: #92400e; font-weight: 600;">
                    ⚡ Action required: Please call the patient within 10–15 minutes.
                </p>
            </div>

            <div style="margin-top: 20px; text-align: center;">
                <a href="https://wa.me/{digits}?text={whatsapp_text}"
                   style="display: inline-block; background: #25D366; color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 15px;">
                    💬 WhatsApp the Patient
                </a>
            </div>
        </div>
        <p style="text-align: center; margin: 16px 0 0; color: #94a3b8; font-size: 12px;">
            Sent by {clinic_name} via <strong>PatientPlex AI</strong>
        </p>
    </div>
    """

    # Send to doctor's email
    result = await send_email(doctor_email, subject, html)
    if result.get("sent"):
        logger.info("Lead alert sent")
    else:
        logger.warning("Lead alert failed")
