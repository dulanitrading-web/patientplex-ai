"""AI-powered WhatsApp receptionist that handles patient conversations and bookings.

This is the CORE differentiator of PatientPlex AI — it uses Claude to conduct
natural conversations with patients and book appointments directly into the
doctor's Google Calendar.

Includes:
- Claude AI with tool-use for natural conversation and booking
- Rule-based fallback when Claude API is unavailable
- Intent classification for analytics
- Urgency detection for emergency prioritisation
- Hinglish (Hindi+English) support for Indian patients
"""

import json
import logging
import re
import uuid
from datetime import datetime, date as date_type, time as time_type, timedelta, timezone
from enum import Enum

import httpx
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversation import (
    Appointment,
    AppointmentStatus,
    Conversation,
    ConversationStatus,
)
from app.models.doctor import Doctor
from app.services.google_calendar import GoogleCalendarService
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

PROMPT_VERSION = "2.0.0"


# ─── Intent Classification ───────────────────────────────────────────────────

class PatientIntent(str, Enum):
    BOOKING = "BOOKING"
    INQUIRY = "INQUIRY"
    COMPLAINT = "COMPLAINT"
    PRICING = "PRICING"
    DIRECTIONS = "DIRECTIONS"
    CANCEL = "CANCEL"
    RESCHEDULE = "RESCHEDULE"
    GREETING = "GREETING"
    EMERGENCY = "EMERGENCY"
    OTHER = "OTHER"


# Patterns checked in order; first match wins
_INTENT_PATTERNS: list[tuple[PatientIntent, list[str]]] = [
    (PatientIntent.EMERGENCY, [
        "emergency", "urgent", "pain right now", "swelling", "bleeding",
        "bahut dard", "dard ho raha", "sujan", "khoon", "toot gaya",
        "broke my tooth", "broken tooth", "accident", "face injury",
    ]),
    (PatientIntent.CANCEL, [
        "cancel", "don't want", "nahi aana", "nahi aa", "cancel karo",
        "cancel kar do", "appointment cancel",
    ]),
    (PatientIntent.RESCHEDULE, [
        "reschedule", "change time", "move appointment", "postpone",
        "badal do", "time change", "shift karo", "doosra din",
    ]),
    (PatientIntent.PRICING, [
        "price", "cost", "fee", "charge", "kitna", "kharcha", "paisa",
        "rate", "kitne paise", "kitna lagega", "insurance", "cashless",
        "how much", "expensive",
    ]),
    (PatientIntent.DIRECTIONS, [
        "address", "direction", "location", "where is", "kahan hai",
        "map", "pata", "navigate", "how to reach", "kaise aaye",
    ]),
    (PatientIntent.BOOKING, [
        "book", "appointment", "slot", "available", "schedule",
        "time milega", "booking", "appoint", "milna hai", "dikhana hai",
        "checkup", "treatment", "consultation", "today", "tomorrow",
        "kal", "aaj", "monday", "tuesday", "parso",
    ]),
    (PatientIntent.COMPLAINT, [
        "complaint", "bad experience", "not happy", "poor", "worst",
        "shikayat", "problem hua", "galat", "unprofessional",
    ]),
    (PatientIntent.GREETING, [
        "hi", "hello", "hey", "namaste", "namaskar", "good morning",
        "good evening", "salam", "hlo", "hii",
    ]),
    (PatientIntent.INQUIRY, [
        "do you", "does", "is there", "can you", "what services",
        "kya karte", "konsi", "what treatment", "kya hota", "batao",
        "tell me", "information", "jaankari",
    ]),
]


def classify_intent(message: str) -> PatientIntent:
    """Classify a patient message into an intent category."""
    msg = message.lower().strip()
    for intent, keywords in _INTENT_PATTERNS:
        if any(kw in msg for kw in keywords):
            return intent
    return PatientIntent.OTHER


def detect_urgency(message: str) -> bool:
    """Return True if the message indicates a dental emergency."""
    msg = message.lower()
    urgent = [
        "emergency", "urgent", "pain right now", "swelling",
        "bleeding", "bahut dard", "dard ho raha", "sujan", "khoon",
        "toot gaya", "broke", "broken tooth", "accident", "face injury",
        "can't eat", "kha nahi pa raha", "neend nahi aa rahi",
    ]
    return any(kw in msg for kw in urgent)


# ─── System Prompt (v2 — Indian context, Hinglish, urgency) ─────────────────

SYSTEM_PROMPT_TEMPLATE = """You are the Business Brain for {clinic_name} — a warm, professional clinic assistant who speaks natural Hinglish.
[Prompt version: {prompt_version}]

Doctor: Dr. {doctor_name}
Specialty: {specialty}
Services: {services}
Address: {address}, {city}
Hours: Mon-Sat, 9 AM to 8 PM

## YOUR PERSONALITY
- Speak natural Hinglish — the way real people in Indian clinics talk. Auto-detect the patient's language from their message and match it. Code-switch naturally between Hindi and English. NOT formal translated Hindi.
- Be warm, respectful (use "ji" with Hindi), and efficient. Keep replies SHORT — 2-3 sentences max.
- You are a helpful assistant, not a doctor. Never pretend to be a medical professional.

## HARD SAFETY RAIL — MEDICAL QUESTIONS
If the patient asks about symptoms, diagnosis, medication, treatment advice, dosage, or any medical question:
→ ALWAYS respond: "Iske liye doctor se baat karna best rahega. Kya main aapka appointment book kar doon?"
→ NEVER give medical advice, suggest treatments, or discuss medications. This is non-negotiable.

If the patient mentions chest pain, difficulty breathing, uncontrolled bleeding, or any life-threatening emergency:
→ IMMEDIATELY respond: "Yeh emergency lagti hai — please turant 112 call karein ya nearest hospital jayein. Doctor ko bhi inform kar deta/deti hoon."
→ Do NOT try to book an appointment for emergencies.

## WHAT YOU CAN DO
1. BOOK APPOINTMENTS: Check available slots (use show_available_slots tool), show numbered options, confirm name + treatment + time, then book (use book_appointment tool).
2. RESCHEDULE/CANCEL: Handle "cancel karo" or "time change" requests.
3. ANSWER CLINIC FAQs: Hours, location, services offered, general price ranges (say "approximately" and suggest confirming with doctor).
4. TAKE MESSAGES: If a patient wants to leave a message for the doctor, note it and confirm.
5. GIVE DIRECTIONS: Share clinic address and Google Maps link.

## HOW TO BOOK
1. When patient wants an appointment → ask what service they need
2. Use show_available_slots to check real availability
3. Present slots as numbered list: "1. 10:00 AM  2. 11:30 AM  3. 4:00 PM"
4. Patient picks a number → confirm: "Dr. {doctor_name} ke saath [treatment] ka appointment [date] ko [time] pe? Name bata dijiye confirm karne ke liye."
5. After patient confirms → use book_appointment tool
6. Send confirmation with address

## PRICING QUESTIONS
When asked "kitna lagega?" → give the range from services list if available, then add: "Final fees doctor consultation ke baad decide hongi." Never invent prices.

## CONVERSATION RULES
- First message greeting: "Namaste! {clinic_name} mein aapka swagat hai. Main aapki kaise madad kar sakti/sakta hoon?"
- Always confirm before booking — never assume.
- If patient says "C" or "cancel" → cancel the ongoing booking flow.
- If you don't understand → ask politely to rephrase, don't guess.
- If asked anything outside your scope → "Main sirf appointment aur clinic info mein help kar sakti/sakta hoon. Doctor se directly baat karne ke liye main message forward kar deti/deta hoon."
"""

CLAUDE_TOOLS = [
    {
        "name": "show_available_slots",
        "description": "Fetch available appointment slots from the doctor's calendar for a specific date. Call this when the patient wants to see available times.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to check in YYYY-MM-DD format. Use today's date if the patient says 'today', tomorrow's if they say 'tomorrow'.",
                }
            },
            "required": ["date"],
        },
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment after confirming patient name, treatment, and time slot. Only call this after the patient has explicitly confirmed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_name": {
                    "type": "string",
                    "description": "Full name of the patient",
                },
                "treatment": {
                    "type": "string",
                    "description": "Treatment or service the patient is interested in",
                },
                "slot_time": {
                    "type": "string",
                    "description": "Selected slot start time in HH:MM format (24h)",
                },
                "slot_date": {
                    "type": "string",
                    "description": "Date of the appointment in YYYY-MM-DD format",
                },
            },
            "required": ["patient_name", "treatment", "slot_time", "slot_date"],
        },
    },
    {
        "name": "get_clinic_directions",
        "description": "Get the clinic address and Google Maps link. Use when a patient asks for directions or location.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the conversation to a human staff member when the patient's request is outside AI capabilities, involves medical advice, complaints, or when the patient explicitly asks to speak to a human.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Brief reason for escalation",
                }
            },
            "required": ["reason"],
        },
    },
]


_CLAUDE_FALLBACK_MARKER = "__CLAUDE_API_UNAVAILABLE__"


class AIReceptionist:
    """Manages a conversational booking flow between a patient and a doctor's AI.

    Uses Claude to understand patient intent, show calendar slots, and book
    appointments — all through WhatsApp.
    """

    def __init__(self, doctor: Doctor, db: AsyncSession):
        self.doctor = doctor
        self.db = db
        self.calendar_service = GoogleCalendarService()
        self._available_slots: list[dict] = []

    async def process_message(self, patient_phone: str, incoming_message: str) -> str:
        """Process an incoming WhatsApp message and return the response.

        This is the main entry point. It:
        1. Gets or creates a conversation record
        2. Classifies intent and detects urgency
        3. Adds the incoming message to history (with intent metadata)
        4. Calls Claude with conversation history + tools
        5. If Claude is down, uses rule-based fallback
        6. Returns the final response text
        """
        conversation = await self._get_or_create_conversation(patient_phone)

        # Classify intent and urgency
        intent = classify_intent(incoming_message)
        is_urgent = detect_urgency(incoming_message)

        # Add incoming message to history with intent metadata
        conversation.messages = conversation.messages + [
            {
                "role": "user",
                "content": incoming_message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "intent": intent.value,
                "urgent": is_urgent,
            }
        ]

        # Update conversation metadata
        if intent == PatientIntent.BOOKING:
            conversation.status = ConversationStatus.BOOKING_IN_PROGRESS
        if is_urgent:
            logger.warning("URGENT patient message from %s: %s", patient_phone, incoming_message[:80])

        # Build Claude messages from conversation history
        claude_messages = self._build_claude_messages(conversation)
        system_prompt = self._build_system_prompt()

        # Call Claude and handle tool use loop
        response_text, total_usage = await self._call_claude_with_tools(
            system_prompt, claude_messages, conversation, patient_phone
        )

        # If Claude returned the generic failure message, use rule-based fallback
        if response_text == _CLAUDE_FALLBACK_MARKER:
            response_text = await self._rule_based_fallback(
                incoming_message, intent, is_urgent, conversation, patient_phone
            )
            total_usage["fallback"] = True

        # Save assistant response to conversation history with metadata
        conversation.messages = conversation.messages + [
            {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt_version": PROMPT_VERSION,
                "usage": total_usage,
            }
        ]
        await self.db.commit()

        return response_text

    # ─── Rule-Based Fallback (when Claude API is down) ───────────────────

    async def _rule_based_fallback(
        self,
        message: str,
        intent: PatientIntent,
        is_urgent: bool,
        conversation: Conversation,
        patient_phone: str,
    ) -> str:
        """Handle patient messages without Claude API using simple decision tree.

        Covers the most common flows: greetings, booking interest, pricing,
        directions, cancellation, and emergencies. Collects patient info
        step by step and creates the appointment when ready.
        """
        doctor = self.doctor
        clinic = doctor.clinic_name or "our clinic"
        services = ", ".join(doctor.services[:5]) if doctor.services else "general consultation"

        if is_urgent:
            return (
                f"I understand you're in pain — we'll help you as soon as possible. 🏥\n\n"
                f"Please call {clinic} directly at {doctor.phone or 'the clinic number'} "
                f"and mention it's urgent. We'll fit you in today.\n\n"
                f"If you'd prefer, reply with your *name* and we'll book the earliest slot for you."
            )

        if intent == PatientIntent.GREETING:
            return (
                f"Namaste! 🙏 Welcome to {clinic}.\n\n"
                f"We offer: {services}.\n\n"
                f"Would you like to book an appointment with Dr. {doctor.full_name}? "
                f"Just tell me which treatment you need!"
            )

        if intent == PatientIntent.PRICING:
            return (
                f"Dr. {doctor.full_name} will discuss the fees during your consultation. "
                f"Most treatments are affordable, and many insurance plans are accepted. 💚\n\n"
                f"Would you like to book an appointment? I can check available slots for you."
            )

        if intent == PatientIntent.DIRECTIONS:
            from urllib.parse import quote_plus
            address = f"{doctor.clinic_address}, {doctor.city}"
            maps_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
            return (
                f"📍 {clinic}\n{address}\n\n"
                f"Google Maps: {maps_link}\n\n"
                f"Would you like to book an appointment?"
            )

        if intent == PatientIntent.CANCEL:
            return (
                f"I'll help you cancel your appointment. "
                f"Could you please share your *name* so I can find your booking? "
                f"Or call the clinic at {doctor.phone or 'the front desk'} to cancel directly."
            )

        if intent == PatientIntent.RESCHEDULE:
            return (
                f"Sure, I can help you reschedule! "
                f"Could you tell me your *name* and which *date/time* works better for you?"
            )

        if intent == PatientIntent.COMPLAINT:
            return (
                f"I'm sorry to hear about your experience. Your feedback matters to us. 🙏\n\n"
                f"I'll make sure Dr. {doctor.full_name} is informed. "
                f"Could you share a few details about what happened?"
            )

        if intent in (PatientIntent.BOOKING, PatientIntent.INQUIRY):
            # Check if we already have enough info to offer slots
            return (
                f"I'd love to help you book an appointment at {clinic}! 📅\n\n"
                f"We offer: {services}.\n\n"
                f"Which treatment are you interested in? And do you prefer *today*, *tomorrow*, or another date?"
            )

        # Catch-all
        return (
            f"Thank you for reaching out to {clinic}! 😊\n\n"
            f"I can help you book an appointment with Dr. {doctor.full_name}. "
            f"What treatment are you looking for?"
        )

    async def _get_or_create_conversation(self, patient_phone: str) -> Conversation:
        """Find active conversation or create a new one."""
        result = await self.db.execute(
            select(Conversation).where(
                and_(
                    Conversation.doctor_id == self.doctor.id,
                    Conversation.patient_phone == patient_phone,
                    Conversation.status.in_([
                        ConversationStatus.ACTIVE,
                        ConversationStatus.BOOKING_IN_PROGRESS,
                    ]),
                )
            ).order_by(Conversation.created_at.desc())
        )
        conversation = result.scalar_one_or_none()

        if conversation is None:
            conversation = Conversation(
                doctor_id=self.doctor.id,
                patient_phone=patient_phone,
                messages=[],
            )
            self.db.add(conversation)
            await self.db.flush()
            logger.info("New conversation created for %s with Dr. %s", patient_phone, self.doctor.full_name)

        return conversation

    def _build_system_prompt(self) -> str:
        services = ", ".join(self.doctor.services or ["General Consultation"])
        return SYSTEM_PROMPT_TEMPLATE.format(
            doctor_name=self.doctor.full_name,
            clinic_name=self.doctor.clinic_name or "Clinic",
            specialty=self.doctor.specialty.value if self.doctor.specialty else "General",
            services=services,
            address=self.doctor.clinic_address or "",
            city=self.doctor.city or "",
            prompt_version=PROMPT_VERSION,
        )

    def _build_claude_messages(self, conversation: Conversation) -> list[dict]:
        """Convert conversation history into Claude API message format."""
        messages = []
        for msg in conversation.messages[-20:]:  # Keep last 20 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        return messages

    async def _call_claude_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        conversation: Conversation,
        patient_phone: str,
    ) -> tuple[str, dict]:
        """Call Claude API with tools and handle the tool-use loop.

        Claude may request tool calls (check slots, book appointment).
        We execute them and feed results back until Claude gives a final text response.

        Returns:
            A tuple of (response_text, usage_dict) where usage_dict contains
            input_tokens, output_tokens, and total_tokens across all iterations.
        """
        current_messages = list(messages)
        max_iterations = 5  # Safety limit on tool-call loops
        total_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

        for _ in range(max_iterations):
            response = await self._call_claude_api(system_prompt, current_messages)
            if response is None:
                return _CLAUDE_FALLBACK_MARKER, total_usage

            # Track token usage
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_usage["input_tokens"] += input_tokens
            total_usage["output_tokens"] += output_tokens
            total_usage["total_tokens"] += input_tokens + output_tokens
            logger.info(
                "Claude API usage — input: %d, output: %d, cumulative total: %d",
                input_tokens, output_tokens, total_usage["total_tokens"],
            )

            # Check if Claude wants to use a tool
            stop_reason = response.get("stop_reason", "end_turn")
            content_blocks = response.get("content", [])

            if stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                assistant_content = []

                for block in content_blocks:
                    if block["type"] == "text":
                        assistant_content.append(block)
                    elif block["type"] == "tool_use":
                        assistant_content.append(block)
                        result = await self._execute_tool(
                            block["name"], block.get("input", {}),
                            conversation, patient_phone,
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": result,
                        })

                # Add assistant message with tool use and tool results
                current_messages.append({"role": "assistant", "content": assistant_content})
                current_messages.append({"role": "user", "content": tool_results})
            else:
                # Final text response
                text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
                response_text = " ".join(text_parts) if text_parts else "How can I help you today?"
                return response_text, total_usage

        return "I'd be happy to help you book an appointment. What treatment are you interested in?", total_usage

    async def _call_claude_api(self, system_prompt: str, messages: list[dict]) -> dict | None:
        """Make a request to an AI API — tries free LLM first, then Claude.

        Priority order:
        1. Free/OpenAI-compatible LLM (Groq, Together, etc.) — saves credits
        2. Claude API — best quality but costs money
        3. None → triggers rule-based fallback
        """
        # Try free LLM first (Groq, Together, Ollama, etc.)
        if settings.FREE_LLM_API_KEY and settings.FREE_LLM_BASE_URL:
            result = await self._call_free_llm(system_prompt, messages)
            if result is not None:
                return result
            logger.warning("Free LLM failed, falling through to Claude API")

        # Try Claude API
        if not settings.CLAUDE_API_KEY:
            logger.warning("No AI API key set (CLAUDE_API_KEY or FREE_LLM_API_KEY) — using fallback")
            return None

        payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "system": system_prompt,
            "tools": CLAUDE_TOOLS,
            "messages": messages,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers={
                        "x-api-key": settings.CLAUDE_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as exc:
            logger.error("Claude API call failed: %s", exc)
            return None

    async def _call_free_llm(self, system_prompt: str, messages: list[dict]) -> dict | None:
        """Call a free/OpenAI-compatible LLM (Groq, Together.ai, etc.) WITH tool use.

        Groq supports OpenAI-compatible function calling, so we convert
        Claude tools to OpenAI format and enable real slot checking + booking.
        """
        # Build OpenAI-format messages
        oai_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            if isinstance(msg.get("content"), str):
                oai_messages.append({"role": msg["role"], "content": msg["content"]})
            elif isinstance(msg.get("content"), list):
                text_parts = []
                for block in msg["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block["text"])
                    elif isinstance(block, dict) and block.get("type") == "tool_result":
                        text_parts.append(str(block.get("content", "")))
                    elif isinstance(block, dict) and block.get("type") == "tool_use":
                        # Convert Claude tool_use to OpenAI function call format
                        text_parts.append(f"[Calling {block.get('name', '')}]")
                if text_parts:
                    oai_messages.append({"role": msg["role"], "content": " ".join(text_parts)})

        # Convert Claude tools to OpenAI function-calling format
        oai_tools = []
        for tool in CLAUDE_TOOLS:
            oai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            })

        payload = {
            "model": settings.FREE_LLM_MODEL,
            "messages": oai_messages,
            "max_tokens": 400,
            "temperature": 0.7,
            "tools": oai_tools,
            "tool_choice": "auto",
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.FREE_LLM_BASE_URL.rstrip('/')}/chat/completions",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.FREE_LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            finish_reason = choice.get("finish_reason", "stop")

            # Handle tool calls from Groq (OpenAI format → Claude format)
            tool_calls = message.get("tool_calls", [])
            if tool_calls and finish_reason == "tool_calls":
                content = []
                for tc in tool_calls:
                    fn = tc.get("function", {})
                    try:
                        args = json.loads(fn.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        args = {}
                    content.append({
                        "type": "tool_use",
                        "id": tc.get("id", f"toolu_{uuid.uuid4().hex[:12]}"),
                        "name": fn.get("name", ""),
                        "input": args,
                    })
                usage = data.get("usage", {})
                return {
                    "content": content,
                    "stop_reason": "tool_use",
                    "usage": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                    },
                }

            # Regular text response
            reply_text = message.get("content", "")
            if not reply_text:
                return None

            usage = data.get("usage", {})
            return {
                "content": [{"type": "text", "text": reply_text}],
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                },
            }
        except Exception as exc:
            logger.error("Free LLM API call failed: %s", exc)
            return None

    async def _execute_tool(
        self,
        tool_name: str,
        tool_input: dict,
        conversation: Conversation,
        patient_phone: str,
    ) -> str:
        """Execute a tool call requested by Claude and return the result as a string."""
        try:
            if tool_name == "show_available_slots":
                return await self._handle_show_slots(tool_input, conversation)
            elif tool_name == "book_appointment":
                return await self._handle_book_appointment(tool_input, conversation, patient_phone)
            elif tool_name == "get_clinic_directions":
                return self._handle_get_directions()
            elif tool_name == "escalate_to_human":
                return await self._handle_escalate_to_human(tool_input, conversation)
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as exc:
            logger.error("Tool execution failed (%s): %s", tool_name, exc)
            return f"Tool error: {str(exc)}"

    async def _handle_escalate_to_human(
        self, tool_input: dict, conversation: Conversation
    ) -> str:
        """Escalate the conversation to a human staff member."""
        reason = tool_input.get("reason", "Patient requested human assistance")

        # Update conversation status
        conversation.status = ConversationStatus.ESCALATED
        await self.db.flush()

        # Notify the doctor via WhatsApp
        if self.doctor.whatsapp_number:
            notification_message = (
                f"[PatientPlex AI] Escalation alert\n"
                f"Patient: {conversation.patient_phone}\n"
                f"Reason: {reason}\n"
                f"Please follow up with the patient directly."
            )
            try:
                await whatsapp_service.send_message(
                    to=self.doctor.whatsapp_number,
                    message=notification_message,
                )
            except Exception as exc:
                logger.error("Failed to notify doctor about escalation: %s", exc)

        logger.info(
            "Conversation %s escalated to human. Reason: %s",
            conversation.id, reason,
        )
        return json.dumps({
            "escalated": True,
            "message": "Escalated to clinic staff. They will be notified immediately.",
        })

    async def _handle_show_slots(self, tool_input: dict, conversation: Conversation) -> str:
        """Fetch available slots from Google Calendar."""
        date_str = tool_input.get("date", "")
        if not date_str:
            return "Please specify a date to check."

        try:
            slots = await self.calendar_service.get_available_slots(
                str(self.doctor.id), date_str, self.db
            )
            self._available_slots = slots
            if not slots:
                return json.dumps({
                    "available": False,
                    "message": f"No available slots on {date_str}",
                    "suggestion": "Try the next day",
                })
            return json.dumps({
                "available": True,
                "date": date_str,
                "slots": slots,
                "count": len(slots),
            })
        except Exception as exc:
            logger.error("Failed to fetch slots: %s", exc)
            # Trigger escalation instead of showing hardcoded fallback slots
            await self._handle_escalate_to_human(
                {"reason": "Calendar service unavailable while checking slots"},
                conversation,
            )
            return json.dumps({
                "available": False,
                "message": "I'm having trouble checking the calendar right now. Let me connect you with the clinic staff to find a slot.",
                "escalated": True,
            })

    async def _handle_book_appointment(
        self, tool_input: dict, conversation: Conversation, patient_phone: str
    ) -> str:
        """Book an appointment and create records."""
        patient_name = tool_input.get("patient_name", "Patient")
        treatment = tool_input.get("treatment", "Consultation")
        slot_time = tool_input.get("slot_time", "10:00")
        slot_date = tool_input.get("slot_date", "")

        # Update conversation
        conversation.patient_name = patient_name
        conversation.treatment_interest = treatment
        conversation.status = ConversationStatus.BOOKED

        # Parse time
        try:
            hour, minute = map(int, slot_time.split(":"))
            appt_time = datetime.strptime(f"{slot_date} {slot_time}", "%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            return json.dumps({"success": False, "error": "Invalid date or time format"})

        # Try to book on Google Calendar
        google_event_id = None
        try:
            result = await self.calendar_service.book_slot(
                str(self.doctor.id),
                appt_time,
                patient_name,
                patient_phone,
                treatment,
                self.db,
            )
            google_event_id = result.get("event_id")
        except Exception as exc:
            logger.warning("Calendar booking failed (will create record anyway): %s", exc)

        # Create appointment record
        from datetime import date as date_type, time as time_type

        appointment = Appointment(
            doctor_id=self.doctor.id,
            conversation_id=conversation.id,
            patient_name=patient_name,
            patient_phone=patient_phone,
            treatment=treatment,
            appointment_date=date_type.fromisoformat(slot_date),
            appointment_time=time_type(hour, minute),
            google_event_id=google_event_id,
            status=AppointmentStatus.CONFIRMED,
        )
        self.db.add(appointment)

        conversation.appointment_datetime = appt_time.replace(tzinfo=timezone.utc)
        await self.db.flush()

        # Send WhatsApp confirmation
        await whatsapp_service.send_booking_confirmation(
            to=patient_phone,
            doctor_name=self.doctor.full_name,
            treatment=treatment,
            date_str=slot_date,
            time_str=slot_time,
            clinic_address=f"{self.doctor.clinic_address}, {self.doctor.city}",
        )

        return json.dumps({
            "success": True,
            "appointment_id": str(appointment.id),
            "doctor": self.doctor.full_name,
            "patient": patient_name,
            "treatment": treatment,
            "date": slot_date,
            "time": slot_time,
            "confirmation_sent": True,
        })

    def _handle_get_directions(self) -> str:
        """Return clinic address and maps link."""
        from urllib.parse import quote_plus

        address = f"{self.doctor.clinic_address}, {self.doctor.city}"
        maps_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
        return json.dumps({
            "address": address,
            "maps_link": maps_link,
            "pincode": self.doctor.pincode or "",
        })
