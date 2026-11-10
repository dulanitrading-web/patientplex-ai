"""WhatsApp webhook and conversation management endpoints."""

import hashlib
import hmac
import logging
import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.auth import get_current_doctor
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, enabled=os.environ.get("TESTING", "").lower() != "true")
from app.db.session import get_db
from app.models.conversation import Appointment, Conversation, ConversationStatus
from app.models.doctor import Doctor
from app.services.ai_receptionist import AIReceptionist
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
@limiter.limit("30/minute")
async def verify_webhook(request: Request):
    """Webhook verification endpoint for WhatsApp/Meta webhook setup.

    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN and challenge:
        logger.info("Webhook verified")
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


async def verify_meta_signature(request: Request) -> None:
    """Validate the X-Hub-Signature-256 header against META_APP_SECRET."""
    app_secret = settings.META_APP_SECRET
    if not app_secret:
        logger.warning(
            "META_APP_SECRET is empty — skipping webhook signature verification (dev mode)"
        )
        return

    signature_header = request.headers.get("X-Hub-Signature-256", "")
    if not signature_header.startswith("sha256="):
        raise HTTPException(status_code=403, detail="Invalid signature format")

    raw_body = await request.body()
    expected = hmac.new(
        app_secret.encode(), raw_body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature_header[7:], expected):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")


@router.post("/webhook", dependencies=[Depends(verify_meta_signature)])
@limiter.limit("30/minute")
async def receive_message(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive incoming WhatsApp messages and process through AI receptionist.

    Handles the Meta Cloud API webhook payload format.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Parse Meta webhook payload
    entries = body.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])

            for message in messages:
                if message.get("type") != "text":
                    continue

                sender_phone = message.get("from", "")
                text = message.get("text", {}).get("body", "")

                if not sender_phone or not text:
                    continue

                # Find which doctor this WhatsApp number belongs to
                doctor = await _find_doctor_by_whatsapp(db, value)
                if doctor is None:
                    logger.warning("No doctor found for incoming message from %s", sender_phone)
                    continue

                # Process through AI receptionist
                receptionist = AIReceptionist(doctor, db)
                response_text = await receptionist.process_message(sender_phone, text)

                # Send response back via WhatsApp
                phone_number_id = value.get("metadata", {}).get("phone_number_id", "")
                await whatsapp_service.send_message(
                    to=sender_phone,
                    message=response_text,
                    phone_number_id=phone_number_id,
                )

    return {"status": "ok"}


async def _find_doctor_by_whatsapp(db: AsyncSession, webhook_value: dict) -> Doctor | None:
    """Find the doctor associated with the receiving WhatsApp business number."""
    phone_number_id = webhook_value.get("metadata", {}).get("phone_number_id", "")
    display_phone = webhook_value.get("metadata", {}).get("display_phone_number", "")

    # Match by WhatsApp number (strip formatting)
    if display_phone:
        clean = display_phone.replace("+", "").replace(" ", "").replace("-", "")
        result = await db.execute(
            select(Doctor).where(Doctor.whatsapp_number.contains(clean[-10:]))
        )
        doctor = result.scalar_one_or_none()
        if doctor:
            return doctor

    logger.warning(
        "No doctor matched WhatsApp business number phone_number_id=%s display=%s — "
        "message will not be processed",
        phone_number_id,
        display_phone,
    )
    return None


# ---- Protected endpoints for doctor dashboard ----

@router.get("/conversations")
async def list_conversations(
    status: ConversationStatus | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the authenticated doctor."""
    query = select(Conversation).where(Conversation.doctor_id == doctor.id)
    if status:
        query = query.where(Conversation.status == status)
    query = query.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    conversations = result.scalars().all()

    return {
        "conversations": [
            {
                "id": str(c.id),
                "patient_phone": c.patient_phone,
                "patient_name": c.patient_name,
                "treatment_interest": c.treatment_interest,
                "status": c.status.value,
                "source": c.source,
                "message_count": len(c.messages),
                "appointment_datetime": c.appointment_datetime.isoformat() if c.appointment_datetime else None,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in conversations
        ],
        "count": len(conversations),
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Get a single conversation with full message history."""
    result = await db.execute(
        select(Conversation).where(
            and_(Conversation.id == conversation_id, Conversation.doctor_id == doctor.id)
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": str(conversation.id),
        "patient_phone": conversation.patient_phone,
        "patient_name": conversation.patient_name,
        "treatment_interest": conversation.treatment_interest,
        "status": conversation.status.value,
        "messages": conversation.messages,
        "source": conversation.source,
        "utm_campaign": conversation.utm_campaign,
        "utm_source": conversation.utm_source,
        "appointment_datetime": conversation.appointment_datetime.isoformat() if conversation.appointment_datetime else None,
        "created_at": conversation.created_at.isoformat(),
    }
