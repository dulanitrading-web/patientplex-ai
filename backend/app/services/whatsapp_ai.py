"""
WhatsApp AI Auto-Reply Service.

Handles incoming patient messages with AI-generated responses.
Supports: OpenAI, Groq, Together.ai, or any OpenAI-compatible API.
Covers appointment booking, treatment enquiries, clinic info, and follow-ups.
"""

import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# AI setup — supports multiple providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FREE_LLM_API_KEY = os.getenv("FREE_LLM_API_KEY", "")
FREE_LLM_BASE_URL = os.getenv("FREE_LLM_BASE_URL", "")
FREE_LLM_MODEL = os.getenv("FREE_LLM_MODEL", "llama-3.3-70b-versatile")

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
        # Try free LLM first (saves credits), then OpenAI
        if FREE_LLM_API_KEY and FREE_LLM_BASE_URL:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(
                    api_key=FREE_LLM_API_KEY,
                    base_url=FREE_LLM_BASE_URL,
                )
                self._model = FREE_LLM_MODEL
                logger.info("WhatsApp AI initialized with free LLM (%s)", FREE_LLM_MODEL)
            except ImportError:
                logger.error("openai package not installed")
            except Exception as e:
                logger.error(f"Free LLM init failed: {e}")
        elif OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
                self._model = "gpt-4o-mini"
                logger.info("WhatsApp AI initialized with OpenAI")
            except ImportError:
                logger.error("openai package not installed")
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")
        else:
            logger.warning("No AI API key set (FREE_LLM_API_KEY or OPENAI_API_KEY) — AI replies use rule-based fallback")

    @property
    def is_active(self) -> bool:
        return self.openai_client is not None

    async def generate_reply(
        self,
        patient_message: str,
        clinic_info: Dict,
        conversation_history: Optional[list] = None,
    ) -> str:
        """Generate an AI reply to a patient's WhatsApp message.

        Uses the comprehensive clinic knowledge base for deep,
        accurate responses about treatments, pricing, and scheduling.
        """
        if not self.is_active:
            return self._fallback_reply(patient_message)

        # Try to use the comprehensive knowledge base
        try:
            from app.services.clinic_knowledge import get_clinic_knowledge, build_ai_system_prompt
            clinic = get_clinic_knowledge(clinic_info.get("clinic_name", ""))
            system = build_ai_system_prompt(clinic)
        except Exception:
            # Fallback to basic prompt if knowledge base fails
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
                model=getattr(self, '_model', 'gpt-4o-mini'),  # Uses free model or OpenAI
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
        """Rule-based fallback when AI is unavailable — uses BDC knowledge."""
        msg_lower = message.lower()

        # Try to get clinic name from knowledge base
        try:
            from app.services.clinic_knowledge import get_clinic_knowledge
            clinic = get_clinic_knowledge()
            clinic_name = clinic.clinic_name
            timings = clinic.timings
            address = clinic.address
            phone = clinic.phone
        except Exception:
            clinic_name = "Bhardwaj Dental Clinic"
            timings = "Mon-Sat 10AM-2PM, 5PM-9PM"
            address = "Nath Mandir Rd, South Tukoganj, Indore"
            phone = "9424488558"

        if any(w in msg_lower for w in ["book", "appointment", "slot", "available", "time", "milna", "aana"]):
            return (
                f"Hii! Appointment ke liye batayein — kab aana chahenge aur kaunsi treatment ke liye?\n\n"
                f"Morning 10-2 ya evening 5-8:30, jo suit kare 😊"
            )
        elif any(w in msg_lower for w in ["price", "cost", "fee", "charge", "kitna", "rate", "paisa", "kharcha", "kitne", "rupee", "rs"]):
            return (
                f"Cost toh doctor check karke hi bata payenge — har case alag hota hai. "
                f"Aap clinic aayein, doctor dekhenge aur poori detail denge.\n\n"
                f"EMI option bhi available hai 😊 Main appointment fix kar doon?"
            )
        elif any(w in msg_lower for w in ["cancel", "reschedule", "change", "badalna"]):
            return (
                f"Haan bilkul! Appointment date aur naya time bata dijiye, main change kar deti hoon 😊"
            )
        elif any(w in msg_lower for w in ["emergency", "urgent", "pain", "bleeding", "accident", "dard", "khoon", "sujan", "swelling", "tut"]):
            return (
                f"Arey! Dard mein bilkul late mat karein — aaj hi aa jayein clinic. "
                f"Dr. Anuj dekhenge, unki specialty yahi hai.\n\n"
                f"Abhi aa sakte hain? Call karein {phone}"
            )
        elif any(w in msg_lower for w in ["hi", "hello", "hey", "namaste", "hii", "helo", "good morning", "good evening"]):
            return (
                f"Hii! 🙏 {clinic_name} se Riya bol rahi hoon. Kaise help karun?"
            )
        elif any(w in msg_lower for w in ["address", "location", "kahan", "jagah", "map", "direction", "kidhar"]):
            return (
                f"Hum South Tukoganj mein hain — Nath Mandir Road pe, Hotel Kalinga ke paas. "
                f"The Horizon building, lower ground floor.\n\n"
                f"Easily mil jayega! Kab aana hai?"
            )
        elif any(w in msg_lower for w in ["timing", "time", "open", "close", "band", "khulta", "samay", "baje"]):
            return (
                f"Monday se Saturday — morning 10 se 2, evening 5 se 8:30. "
                f"Sunday chutti 😊\n\nKaunsa din suit karega?"
            )
        elif any(w in msg_lower for w in ["doctor", "kaun", "specialist", "kon"]):
            return (
                f"Humare paas 5 specialist doctors hain — Orthodontist, Endodontist, Prosthodontist sab ek jagah. "
                f"Aapki problem batayein, main sahi doctor se milwa dungi 😊"
            )
        elif any(w in msg_lower for w in ["thank", "thanks", "dhanyawad", "shukriya", "ok", "okay", "theek"]):
            return (
                f"Welcome ji! 🙏 Kuch aur help chahiye toh batayein. Have a great day!"
            )
        else:
            return (
                f"Hii! Main Riya hoon, {clinic_name} se. "
                f"Aapka message mil gaya — batayein kaise help karun? "
                f"Appointment fix karna hai ya koi aur jaankari chahiye?"
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
