"""Email service for appointment confirmations, reminders, and digests.

Supports SMTP (Gmail, Zoho, etc.) and Resend API.
Gracefully degrades if not configured — logs the skip instead of failing.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def _is_configured() -> bool:
    """Check if any email provider is configured."""
    if settings.EMAIL_PROVIDER == "resend" and settings.RESEND_API_KEY:
        return True
    if settings.EMAIL_PROVIDER == "smtp" and settings.SMTP_HOST and settings.SMTP_USER:
        return True
    return False


async def send_email(to: str, subject: str, html_body: str, text_body: str = "") -> dict:
    """Send an email via the configured provider.

    Returns {"sent": True/False, "reason": "..."}.
    """
    if not _is_configured():
        logger.debug("Email not configured — skipping: %s to %s", subject, to)
        return {"sent": False, "reason": "Email not configured"}

    if not to or "@" not in to:
        return {"sent": False, "reason": "Invalid recipient email"}

    from_name = settings.EMAIL_FROM_NAME
    from_addr = settings.EMAIL_FROM_ADDRESS or settings.SMTP_USER

    if settings.EMAIL_PROVIDER == "resend":
        return await _send_resend(to, subject, html_body, from_name, from_addr)
    else:
        return await _send_smtp(to, subject, html_body, text_body, from_name, from_addr)


async def _send_resend(to: str, subject: str, html: str, from_name: str, from_addr: str) -> dict:
    """Send via Resend API."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                json={
                    "from": f"{from_name} <{from_addr}>",
                    "to": [to],
                    "subject": subject,
                    "html": html,
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                logger.info("Email sent via Resend: %s → %s", subject, to)
                return {"sent": True}
            else:
                logger.warning("Resend error %s: %s", resp.status_code, resp.text)
                return {"sent": False, "reason": f"Resend error: {resp.status_code}"}
    except Exception as exc:
        logger.error("Resend exception: %s", exc)
        return {"sent": False, "reason": str(exc)}


async def _send_smtp(to: str, subject: str, html: str, text: str, from_name: str, from_addr: str) -> dict:
    """Send via SMTP (runs in thread to avoid blocking the event loop)."""
    import asyncio

    def _send():
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{from_name} <{from_addr}>"
        msg["To"] = to
        msg["Subject"] = subject

        if text:
            msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.ehlo()
                if settings.SMTP_PORT != 25:
                    server.starttls()
                    server.ehlo()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(from_addr, [to], msg.as_string())
            logger.info("Email sent via SMTP: %s → %s", subject, to)
            return {"sent": True}
        except Exception as exc:
            logger.error("SMTP error: %s", exc)
            return {"sent": False, "reason": str(exc)}

    return await asyncio.get_event_loop().run_in_executor(None, _send)


# ─── Appointment Email Templates ───


async def send_appointment_confirmation(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    clinic_name: str,
    treatment: str,
    date_str: str,
    time_str: str,
    clinic_address: str = "",
    clinic_phone: str = "",
) -> dict:
    """Send appointment confirmation email to patient."""
    subject = f"Appointment Confirmed — {clinic_name}"
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px;">
        <div style="background: #10b981; color: white; padding: 16px 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0; font-size: 18px;">✅ Appointment Confirmed</h2>
        </div>
        <div style="border: 1px solid #e2e8f0; border-top: none; padding: 24px; border-radius: 0 0 12px 12px;">
            <p style="margin: 0 0 16px; color: #334155;">Hi <strong>{patient_name}</strong>,</p>
            <p style="margin: 0 0 20px; color: #334155;">Your appointment has been confirmed:</p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px 0; color: #64748b; width: 120px;">Doctor</td><td style="padding: 8px 0; color: #0f172a; font-weight: 600;">{doctor_name}</td></tr>
                <tr><td style="padding: 8px 0; color: #64748b;">Treatment</td><td style="padding: 8px 0; color: #0f172a; font-weight: 600;">{treatment}</td></tr>
                <tr><td style="padding: 8px 0; color: #64748b;">Date</td><td style="padding: 8px 0; color: #0f172a; font-weight: 600;">{date_str}</td></tr>
                <tr><td style="padding: 8px 0; color: #64748b;">Time</td><td style="padding: 8px 0; color: #0f172a; font-weight: 600;">{time_str}</td></tr>
                {"<tr><td style='padding: 8px 0; color: #64748b;'>Address</td><td style='padding: 8px 0; color: #0f172a;'>" + clinic_address + "</td></tr>" if clinic_address else ""}
                {"<tr><td style='padding: 8px 0; color: #64748b;'>Phone</td><td style='padding: 8px 0; color: #0f172a;'>" + clinic_phone + "</td></tr>" if clinic_phone else ""}
            </table>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="margin: 0; color: #64748b; font-size: 13px;">Need to reschedule? Reply to this email or call the clinic.</p>
        </div>
        <p style="text-align: center; margin: 16px 0 0; color: #94a3b8; font-size: 12px;">Sent by {clinic_name} via PatientPlex AI</p>
    </div>
    """
    return await send_email(patient_email, subject, html)


async def send_appointment_reminder(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    clinic_name: str,
    treatment: str,
    date_str: str,
    time_str: str,
    hours_before: int = 24,
) -> dict:
    """Send appointment reminder email."""
    subject = f"Reminder: Appointment Tomorrow — {clinic_name}"
    if hours_before <= 4:
        subject = f"Reminder: Appointment Today at {time_str} — {clinic_name}"

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px;">
        <div style="background: #f59e0b; color: white; padding: 16px 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0; font-size: 18px;">⏰ Appointment Reminder</h2>
        </div>
        <div style="border: 1px solid #e2e8f0; border-top: none; padding: 24px; border-radius: 0 0 12px 12px;">
            <p style="margin: 0 0 16px; color: #334155;">Hi <strong>{patient_name}</strong>,</p>
            <p style="margin: 0 0 20px; color: #334155;">This is a friendly reminder about your upcoming appointment:</p>
            <div style="background: #fefce8; border: 1px solid #fde68a; border-radius: 8px; padding: 16px;">
                <p style="margin: 0; color: #92400e;"><strong>{treatment}</strong> with <strong>{doctor_name}</strong></p>
                <p style="margin: 8px 0 0; color: #92400e; font-size: 18px; font-weight: 700;">{date_str} at {time_str}</p>
            </div>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="margin: 0; color: #64748b; font-size: 13px;">Can't make it? Please let us know so we can offer the slot to another patient.</p>
        </div>
        <p style="text-align: center; margin: 16px 0 0; color: #94a3b8; font-size: 12px;">Sent by {clinic_name} via PatientPlex AI</p>
    </div>
    """
    return await send_email(patient_email, subject, html)


email_service_configured = _is_configured
