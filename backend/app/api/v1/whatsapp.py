"""WhatsApp webhook and conversation management endpoints."""

import asyncio
import hashlib
import hmac
import logging
import os
from collections import OrderedDict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.auth import get_current_doctor
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, enabled=os.environ.get("TESTING", "").lower() != "true")
from app.db.session import get_db, async_session_factory
from app.models.conversation import Appointment, Conversation, ConversationStatus
from app.models.doctor import Doctor
from app.services.ai_receptionist import AIReceptionist
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

# --- Idempotency: dedupe Meta webhook message IDs (in-memory LRU) ---
_seen_message_ids: OrderedDict[str, bool] = OrderedDict()
_SEEN_MAX = 5000


def _is_duplicate_message(message_id: str) -> bool:
    """Check if we've already processed this Meta message ID. Thread-safe for asyncio."""
    if not message_id:
        return False
    if message_id in _seen_message_ids:
        return True
    _seen_message_ids[message_id] = True
    while len(_seen_message_ids) > _SEEN_MAX:
        _seen_message_ids.popitem(last=False)
    return False

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
        env = os.environ.get("ENVIRONMENT", "development")
        if env in ("production", "staging"):
            logger.error("META_APP_SECRET is empty in production — rejecting webhook")
            raise HTTPException(status_code=403, detail="Webhook verification not configured")
        logger.warning(
            "META_APP_SECRET is empty — skipping signature verification (dev mode only)"
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
@limiter.limit("60/minute")
async def receive_message(request: Request):
    """Receive incoming WhatsApp messages and process through AI receptionist.

    Returns 200 immediately and processes messages in a background task.
    Meta retries on timeout, so fast response is critical.
    Deduplicates on message ID to prevent double-processing.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Parse Meta webhook payload — collect messages to process
    tasks_to_run = []
    entries = body.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])

            for message in messages:
                msg_id = message.get("id", "")

                # Idempotency: skip already-processed messages
                if _is_duplicate_message(msg_id):
                    logger.info("Skipping duplicate message %s", msg_id)
                    continue

                if message.get("type") != "text":
                    logger.info("Ignoring non-text WhatsApp message")
                    continue

                sender_phone = message.get("from", "")
                text = message.get("text", {}).get("body", "")
                phone_number_id = value.get("metadata", {}).get("phone_number_id", "")
                display_phone = value.get("metadata", {}).get("display_phone_number", "")

                if not sender_phone or not text:
                    continue

                tasks_to_run.append({
                    "sender_phone": sender_phone,
                    "text": text,
                    "phone_number_id": phone_number_id,
                    "display_phone": display_phone,
                })

    # Fire background tasks for each message — don't block the 200 response
    for task_data in tasks_to_run:
        asyncio.create_task(_process_whatsapp_message(
            sender_phone=task_data["sender_phone"],
            text=task_data["text"],
            phone_number_id=task_data["phone_number_id"],
            display_phone=task_data["display_phone"],
        ))

    return {"status": "ok"}


async def _process_whatsapp_message(
    sender_phone: str,
    text: str,
    phone_number_id: str,
    display_phone: str,
) -> None:
    """Background task: process a WhatsApp message through AI receptionist.

    Uses its own DB session since the request session is closed after 200.
    Retries WhatsApp send with backoff on failure.
    """
    try:
        async with async_session_factory() as db:
            # Find which doctor this WhatsApp number belongs to
            doctor = await _find_doctor_by_whatsapp(db, {
                "metadata": {
                    "phone_number_id": phone_number_id,
                    "display_phone_number": display_phone,
                }
            })
            if doctor is None:
                logger.warning("No clinic matched incoming WhatsApp message")
                return

            # Process through AI receptionist
            receptionist = AIReceptionist(doctor, db)
            response_text = await receptionist.process_message(sender_phone, text)

            # Send response back via WhatsApp — retry with backoff
            await _send_with_retry(
                to=sender_phone,
                message=response_text,
                phone_number_id=phone_number_id,
            )
    except Exception as exc:
        logger.error("WhatsApp processing failed: %s", type(exc).__name__)


async def _send_with_retry(
    to: str,
    message: str,
    phone_number_id: str,
    max_attempts: int = 3,
    backoff_seconds: tuple[int, ...] = (30, 120, 600),
) -> dict:
    """Send a WhatsApp message with exponential backoff retry.

    Retries on failure: 30s, 2min, 10min.
    """
    for attempt in range(max_attempts):
        result = await whatsapp_service.send_message(
            to=to, message=message, phone_number_id=phone_number_id,
        )
        if "error" not in result:
            return result
        if attempt < max_attempts - 1:
            delay = backoff_seconds[attempt] if attempt < len(backoff_seconds) else backoff_seconds[-1]
            logger.warning(
                "WhatsApp send to %s failed (attempt %d/%d), retrying in %ds: %s",
                to, attempt + 1, max_attempts, delay, result.get("error"),
            )
            await asyncio.sleep(delay)
        else:
            logger.error(
                "WhatsApp send to %s failed after %d attempts: %s",
                to, max_attempts, result.get("error"),
            )
    return result


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
