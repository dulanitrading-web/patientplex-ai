"""
WhatsApp AI Auto-Reply Service.

Handles incoming patient messages with AI-generated responses using OpenAI.
Covers appointment booking, treatment enquiries, clinic info, and follow-ups.
"""

import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """You are the AI receptionist for {clinic_name}, a {specialty} clinic.

Your job:
1. Answer patient enquiries warmly and professionally
2. Provide treatment information and pricing when asked
3. Help patients book appointments by asking for preferred date/time
4. Collect patient name and phone number if not already known
5. Handle rescheduling and cancellation requests
6. For medical emergencies, immediately advise calling 108 or visiting the nearest hospital

Clinic details:
- Name: {clinic_name}
- Doctor: {doctor_name}
- Specialty: {specialty}
- Location: {location}
- Timings: {timings}
- Treatments: {treatments}

Rules:
- Be warm, use the patient's name when known
- Keep responses concise (under 150 words)
- Use Hindi words naturally if the patient writes in Hindi (e.g., "Namaste", "ji")
- Never give medical diagnoses — always recommend an in-person consultation
- If unsure, say you'll check with the doctor and get back
- Always end with a clear next step (book an appointment, visit the clinic, etc.)
"""


class WhatsAppAI:
    """AI-powered auto-reply for WhatsApp patient messages."""

    def __init__(self):
        self.openai_client = None
        self._initialize()

    def _initialize(self):
        if OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
                logger.info("WhatsApp AI initialized with OpenAI")
            except ImportError:
                logger.error("openai package not installed")
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")
        else:
            logger.warning("OPENAI_API_KEY not set — AI replies disabled")

    @property
    def is_active(self) -> bool:
        return self.openai_client is not None

    async def generate_reply(
        self,
        patient_message: str,
        clinic_info: Dict,
        conversation_history: Optional[list] = None,
    ) -> str:
        """Generate an AI reply to a patient's WhatsApp message."""
        if not self.is_active:
            return self._fallback_reply(patient_message)

        system = SYSTEM_PROMPT.format(
            clinic_name=clinic_info.get("clinic_name", "the clinic"),
            doctor_name=clinic_info.get("doctor_name", "the doctor"),
            specialty=clinic_info.get("specialty", "general practice"),
            location=clinic_info.get("location", ""),
            timings=clinic_info.get("timings", "Mon-Sat, 9am-7pm"),
            treatments=clinic_info.get("treatments", "General consultations"),
        )

        messages = [{"role": "system", "content": system}]

        # Add conversation history for context
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": "user" if msg["from"] == "patient" else "assistant",
                    "content": msg["text"],
                })

        messages.append({"role": "user", "content": patient_message})

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective for chat
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            logger.info(f"AI reply generated ({len(reply)} chars)")
            return reply
        except Exception as e:
            logger.error(f"AI reply generation failed: {e}")
            return self._fallback_reply(patient_message)

    def _fallback_reply(self, message: str) -> str:
        """Rule-based fallback when AI is unavailable."""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["book", "appointment", "slot", "available", "time"]):
            return (
                "Thank you for your interest! 🙏\n\n"
                "To book an appointment, please share:\n"
                "1. Your preferred date\n"
                "2. Morning or evening slot\n"
                "3. Treatment you're looking for\n\n"
                "Our team will confirm your appointment shortly."
            )
        elif any(w in msg_lower for w in ["price", "cost", "fee", "charge", "kitna", "rate"]):
            return (
                "Thank you for asking! Treatment costs vary based on the procedure.\n\n"
                "I'd recommend scheduling a consultation so the doctor can "
                "assess your needs and give you an accurate estimate.\n\n"
                "Shall I book a consultation for you?"
            )
        elif any(w in msg_lower for w in ["cancel", "reschedule", "change"]):
            return (
                "I understand you'd like to make a change to your appointment.\n\n"
                "Please share your appointment date and the new preferred time, "
                "and I'll update it for you right away."
            )
        elif any(w in msg_lower for w in ["emergency", "urgent", "pain", "bleeding", "accident"]):
            return (
                "⚠️ If this is a medical emergency, please call 108 immediately "
                "or go to the nearest hospital.\n\n"
                "For urgent but non-emergency concerns, we'll try to fit you in today. "
                "Can you describe what's happening?"
            )
        elif any(w in msg_lower for w in ["hi", "hello", "hey", "namaste"]):
            return (
                "Namaste! 🙏 Welcome to our clinic.\n\n"
                "How can I help you today? I can:\n"
                "• Book an appointment\n"
                "• Share treatment information\n"
                "• Answer your questions\n\n"
                "What would you like to know?"
            )
        else:
            return (
                "Thank you for your message! 🙏\n\n"
                "I'll check with the doctor and get back to you shortly. "
                "In the meantime, would you like to book an appointment?"
            )

    async def detect_intent(self, message: str) -> str:
        """Detect the intent of a patient message."""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["book", "appointment", "slot", "available"]):
            return "booking"
        elif any(w in msg_lower for w in ["cancel", "reschedule"]):
            return "reschedule"
        elif any(w in msg_lower for w in ["price", "cost", "fee", "kitna"]):
            return "pricing"
        elif any(w in msg_lower for w in ["emergency", "urgent", "pain"]):
            return "emergency"
        elif any(w in msg_lower for w in ["hi", "hello", "hey", "namaste"]):
            return "greeting"
        elif any(w in msg_lower for w in ["thank", "thanks", "dhanyavaad"]):
            return "gratitude"
        else:
            return "general"


whatsapp_ai = WhatsAppAI()
