"""AI-powered WhatsApp receptionist that handles patient conversations and bookings.

This is the CORE differentiator of PatientPlex AI — it uses Claude to conduct
natural conversations with patients and book appointments directly into the
doctor's Google Calendar.
"""

import json
import logging
import uuid
from datetime import datetime, timezone

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

SYSTEM_PROMPT_TEMPLATE = """You are a friendly, professional AI receptionist for Dr. {doctor_name}'s {clinic_name}.
Specialty: {specialty}
Services offered: {services}
Clinic address: {address}, {city}

Your ONLY job is to help patients book appointments. You must NEVER:
- Give medical advice or diagnoses
- Recommend treatments or medications
- Discuss pricing (say "the doctor will discuss this during your visit")
- Share other patient information
- Make up information about the doctor

RULES:
- Keep responses SHORT (2-3 sentences max). Be warm but efficient.
- When the patient shows interest in a service, offer to check available slots.
- When showing slots, present them as a numbered list and ask which one works.
- Always confirm: patient name, treatment interest, and chosen slot before booking.
- Respond in the same language the patient uses (Hindi, Telugu, English, etc.)
- If the patient asks something outside your scope, politely redirect to booking.
- If the patient says CANCEL, RESCHEDULE, or similar, handle accordingly.
- Use the tools provided to check slots and book appointments.
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
]


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
        2. Adds the incoming message to history
        3. Calls Claude with conversation history + tools
        4. Handles any tool calls (slot lookup, booking)
        5. Returns the final response text
        """
        conversation = await self._get_or_create_conversation(patient_phone)

        # Add incoming message to history
        conversation.messages = conversation.messages + [
            {"role": "user", "content": incoming_message, "timestamp": datetime.now(timezone.utc).isoformat()}
        ]

        # Build Claude messages from conversation history
        claude_messages = self._build_claude_messages(conversation)
        system_prompt = self._build_system_prompt()

        # Call Claude and handle tool use loop
        response_text = await self._call_claude_with_tools(
            system_prompt, claude_messages, conversation, patient_phone
        )

        # Save assistant response to conversation history
        conversation.messages = conversation.messages + [
            {"role": "assistant", "content": response_text, "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        await self.db.commit()

        return response_text

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
    ) -> str:
        """Call Claude API with tools and handle the tool-use loop.

        Claude may request tool calls (check slots, book appointment).
        We execute them and feed results back until Claude gives a final text response.
        """
        current_messages = list(messages)
        max_iterations = 5  # Safety limit on tool-call loops

        for _ in range(max_iterations):
            response = await self._call_claude_api(system_prompt, current_messages)
            if response is None:
                return "Sorry, I'm having trouble right now. Please try again in a moment."

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
                return " ".join(text_parts) if text_parts else "How can I help you today?"

        return "I'd be happy to help you book an appointment. What treatment are you interested in?"

    async def _call_claude_api(self, system_prompt: str, messages: list[dict]) -> dict | None:
        """Make a request to the Claude Messages API."""
        if not settings.CLAUDE_API_KEY:
            logger.warning("CLAUDE_API_KEY not set — using fallback response")
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
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as exc:
            logger.error("Tool execution failed (%s): %s", tool_name, exc)
            return f"Tool error: {str(exc)}"

    async def _handle_show_slots(self, tool_input: dict, conversation: Conversation) -> str:
        """Fetch available slots from Google Calendar."""
        date_str = tool_input.get("date", "")
        if not date_str:
            return "Please specify a date to check."

        try:
            slots = await self.calendar_service.get_available_slots(
                str(self.doctor.id), date_str
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
            return json.dumps({
                "available": True,
                "date": date_str,
                "slots": [
                    {"start": "09:00", "end": "09:30"},
                    {"start": "10:00", "end": "10:30"},
                    {"start": "11:30", "end": "12:00"},
                    {"start": "14:00", "end": "14:30"},
                    {"start": "15:30", "end": "16:00"},
                    {"start": "17:00", "end": "17:30"},
                ],
                "count": 6,
                "note": "Showing default slots (calendar not connected)",
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
