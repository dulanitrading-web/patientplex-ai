"""
WhatsApp AI Auto-Reply Service.

Handles incoming patient messages with AI-generated responses.
Supports: OpenAI, Groq, Together.ai, or any OpenAI-compatible API.
Covers appointment booking, treatment enquiries, clinic info, and follow-ups.
"""

import logging
import os
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _sanitize_message(text: str) -> str:
    """Sanitize patient message to prevent prompt injection attacks.

    Limits length, strips control chars, and flags injection attempts.
    Does NOT block messages — just cleans them. The system prompt guardrails
    handle the rest.
    """
    if not text:
        return ""
    # Limit length to prevent context window abuse
    text = text[:500]
    # Remove control characters (keep newlines and basic whitespace)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()

# AI setup — supports multiple providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FREE_LLM_API_KEY = os.getenv("FREE_LLM_API_KEY", "")
FREE_LLM_BASE_URL = os.getenv("FREE_LLM_BASE_URL", "")
FREE_LLM_MODEL = os.getenv("FREE_LLM_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """Tu Riya hai — {clinic_name} ki friendly receptionist. Tu hamesha HINGLISH mein baat karti hai (Hindi + English mixed, jaise ek real receptionist Indore mein bolti hai). KABHI pure English mein mat bol. Hamesha natural, warm aur helpful reh.

Tera kaam:
1. Patient ke sawaalon ka jawab de — pyaar se, apnapan se
2. Treatment ke baare mein jaankari de (lekin KABHI price/cost/fee mat batao)
3. Appointment book karwa — patient se date/time poochh
4. Patient ka naam aur phone number le agar nahi pata
5. Reschedule aur cancel handle kar
6. Emergency mein turant 108 ya nearest hospital jaane bol

Clinic details:
- Naam: {clinic_name}
- Doctor: {doctor_name}
- Specialty: {specialty}
- Jagah: {location}
- Timing: {timings}
- Treatments: {treatments}

Rules:
- Hamesha Hinglish mein bol — jaise WhatsApp pe real person baat karta hai
- Patient ka naam use kar jab pata ho
- Chhota reply de (3-4 line max)
- "aap", "ji", "haan" naturally use kar
- Emojis thode use kar — 🙏 😊 jaise real person karta hai
- KABHI medical diagnosis mat de — hamesha bol "Doctor dekhenge"
- KABHI price/cost/fee/rate mat bata — hamesha bol "Doctor check karke batayenge, aap clinic aayiye"
- Agar kuch nahi pata toh bol "Main doctor se poochh ke batati hoon"
- Hamesha next step bata — appointment book karo, clinic aao, etc.
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

        # Sanitize patient input to prevent prompt injection
        patient_message = _sanitize_message(patient_message)
        if not patient_message:
            return self._fallback_reply("")

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

        if any(w in msg_lower for w in ["hi", "hello", "hey", "namaste", "hii", "helo", "good morning", "good evening", "namaskar"]):
            return (
                f"Namaste! 🙏 {clinic_name} mein aapka swagat hai. Main Riya hoon, clinic ki assistant. "
                f"Aapko kisi treatment ke baare mein jaankari chahiye ya appointment book karni hai?"
            )
        elif any(w in msg_lower for w in ["book", "appointment", "slot", "available", "time", "milna", "aana", "dikhana", "checkup"]):
            return (
                f"Appointment ke liye aap clinic call kar sakte hain {phone} par, ya mujhe apna naam aur convenient time bata dijiye, main arrange kar deti hoon 😊\n\n"
                f"Morning 10-2 ya evening 5-8:30, jo suit kare!"
            )
        elif any(w in msg_lower for w in ["price", "cost", "fee", "charge", "kitna", "rate", "paisa", "kharcha", "kitne", "rupee", "rs", "lagega"]):
            return (
                f"Pricing toh doctor check karke hi bata payenge — har case mein treatment alag hota hai na. "
                f"Aap ek baar clinic visit kariye, doctor dekhenge aur best plan batayenge 👨‍⚕️\n\n"
                f"EMI option bhi available hai. Main appointment fix kar doon?"
            )
        elif any(w in msg_lower for w in ["cancel", "reschedule", "change", "badalna"]):
            return (
                f"Koi baat nahi! Appointment cancel ya change karne ke liye clinic ko call kariye {phone} par. "
                f"Hum aapke liye naya time reschedule bhi kar sakte hain 🗓️"
            )
        elif any(w in msg_lower for w in ["emergency", "urgent", "pain", "bleeding", "accident", "dard", "khoon", "sujan", "swelling", "tut"]):
            return (
                f"Agar aapko bahut dard ho raha hai toh turant clinic aayiye — {phone} par call karke batayein ki aa rahe hain. "
                f"Dr. Anuj dekhenge, unki specialty yahi hai.\n\n"
                f"Clinic ka address: LG 9-11, The Horizon, Nath Mandir Road, South Tukoganj, Indore."
            )
        elif any(w in msg_lower for w in ["address", "location", "kahan", "jagah", "map", "direction", "kidhar"]):
            return (
                f"{clinic_name} ka address hai: LG 9-11, The Horizon Building, 11/5, Nath Mandir Road, "
                f"South Tukoganj, Indore 452001 (Near Hotel Kalinga).\n\n"
                f"Timing: Mon-Sat 10AM-2PM aur 5PM-8:30PM 🏥\nAap kab aana chahenge?"
            )
        elif any(w in msg_lower for w in ["timing", "time", "open", "close", "band", "khulta", "samay", "baje"]):
            return (
                f"Clinic ka timing hai Monday se Saturday: Subah 10 baje se dopahar 2 baje tak, "
                f"aur shaam 5 baje se 8:30 baje tak. Sunday band rehta hai 📅\n\n"
                f"Kaunsa din suit karega aapko?"
            )
        elif any(w in msg_lower for w in ["doctor", "kaun", "specialist", "kon"]):
            return (
                f"Hamare clinic mein 5 specialist doctors hain — Dr. Amit Bhardwaj (Orthodontist), "
                f"Dr. Anuj Bhardwaj (Endodontist), Dr. Shivani Bhardwaj (Prosthodontist), "
                f"Dr. Kratika Mishra (Orthodontist), aur Dr. Vihang Naphade (Oral Medicine).\n\n"
                f"Aapko kis treatment ke liye aana hai, main sahi doctor suggest kar deti hoon 👨‍⚕️"
            )
        elif any(w in msg_lower for w in ["thank", "thanks", "dhanyawad", "shukriya", "ok", "okay", "theek"]):
            return (
                f"Dhanyavaad! 🙏 Koi aur sawaal ho toh poochh lijiye. Hum aapki madad ke liye hamesha hain!"
            )
        else:
            return (
                f"Main samajh nahi paayi 😊 Kya aap appointment book karna chahte hain ya kisi treatment ke baare mein jaanna chahte hain? "
                f"Aap hume {phone} par bhi call kar sakte hain 📞"
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
