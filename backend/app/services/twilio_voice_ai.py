"""
Twilio Voice AI Agent — Handles incoming calls with an AI voice receptionist.

Uses Twilio <Gather> + OpenAI to create a conversational phone experience:
1. Answer with a greeting
2. Listen to caller's speech
3. AI generates a response
4. Speak the response using Twilio <Say>
5. Loop until booking is complete or caller hangs up
"""

import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

VOICE_SYSTEM_PROMPT = """You are the phone receptionist for {clinic_name}, a {specialty} clinic run by {doctor_name}.

You are speaking on the phone, so:
- Keep responses SHORT (2-3 sentences max)
- Be warm and natural — speak like a friendly Indian receptionist
- Use simple language, no jargon
- Say "ji" naturally where appropriate
- For appointment booking, ask for: name, preferred date, preferred time, treatment needed
- For emergencies, say "Please call 108 or go to the nearest hospital immediately"
- If they want to speak to the doctor directly, say you'll transfer them

Clinic timings: {timings}
Location: {location}
"""


class TwilioVoiceAI:
    """AI-powered voice receptionist using Twilio + OpenAI."""

    def __init__(self):
        self.openai_client = None
        self.twilio_client = None
        self._initialize()

    def _initialize(self):
        if OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            except (ImportError, Exception) as e:
                logger.error(f"OpenAI init failed: {e}")

        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                logger.info("Twilio Voice AI initialized")
            except (ImportError, Exception) as e:
                logger.error(f"Twilio init failed: {e}")

    @property
    def is_active(self) -> bool:
        return self.twilio_client is not None

    def generate_greeting_twiml(self, clinic_name: str, webhook_url: str) -> str:
        """Generate TwiML for initial call greeting with Gather for speech input."""
        from twilio.twiml.voice_response import VoiceResponse, Gather

        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action=f"{webhook_url}/api/v1/calls/gather",
            method="POST",
            language="hi-IN",  # Hindi (with English fallback)
            speech_timeout="3",
            timeout=5,
        )
        gather.say(
            f"Namaste! Thank you for calling {clinic_name}. "
            "I'm the AI assistant and can help you book an appointment, "
            "answer questions, or connect you with the doctor. "
            "How can I help you today?",
            voice="Polly.Aditi",  # Indian English voice
            language="en-IN",
        )
        response.append(gather)

        # If no input, repeat
        response.redirect(f"{webhook_url}/api/v1/calls/incoming", method="POST")
        return str(response)

    async def process_speech_and_respond(
        self,
        speech_result: str,
        clinic_info: Dict,
        webhook_url: str,
        conversation_history: Optional[list] = None,
    ) -> str:
        """Process caller's speech, generate AI reply, return TwiML."""
        from twilio.twiml.voice_response import VoiceResponse, Gather

        # Generate AI response
        ai_reply = await self._generate_voice_reply(speech_result, clinic_info, conversation_history)

        response = VoiceResponse()

        # Check if we should transfer to doctor
        if "[TRANSFER]" in ai_reply:
            ai_reply = ai_reply.replace("[TRANSFER]", "").strip()
            response.say(ai_reply, voice="Polly.Aditi", language="en-IN")
            doctor_phone = clinic_info.get("doctor_phone", "")
            if doctor_phone:
                response.say(
                    "Transferring you to the doctor now. Please hold.",
                    voice="Polly.Aditi", language="en-IN",
                )
                response.dial(doctor_phone, timeout=30)
            else:
                response.say(
                    "I'm sorry, the doctor is currently unavailable. "
                    "I'll have them call you back as soon as possible.",
                    voice="Polly.Aditi", language="en-IN",
                )
            return str(response)

        # Check if booking is complete
        if "[BOOKED]" in ai_reply:
            ai_reply = ai_reply.replace("[BOOKED]", "").strip()
            response.say(ai_reply, voice="Polly.Aditi", language="en-IN")
            response.say(
                "Thank you for calling. We look forward to seeing you. Goodbye!",
                voice="Polly.Aditi", language="en-IN",
            )
            response.hangup()
            return str(response)

        # Continue conversation
        gather = Gather(
            input="speech",
            action=f"{webhook_url}/api/v1/calls/gather",
            method="POST",
            language="hi-IN",
            speech_timeout="3",
            timeout=8,
        )
        gather.say(ai_reply, voice="Polly.Aditi", language="en-IN")
        response.append(gather)

        # If no input after response, ask if they're still there
        response.say(
            "Are you still there? If you need anything else, please speak now.",
            voice="Polly.Aditi", language="en-IN",
        )
        response.hangup()

        return str(response)

    async def _generate_voice_reply(
        self,
        caller_speech: str,
        clinic_info: Dict,
        conversation_history: Optional[list] = None,
    ) -> str:
        """Generate AI reply for voice conversation."""
        if not self.openai_client:
            return self._fallback_voice_reply(caller_speech)

        system = VOICE_SYSTEM_PROMPT.format(
            clinic_name=clinic_info.get("clinic_name", "the clinic"),
            doctor_name=clinic_info.get("doctor_name", "the doctor"),
            specialty=clinic_info.get("specialty", "general"),
            timings=clinic_info.get("timings", "Mon-Sat 9am-7pm"),
            location=clinic_info.get("location", ""),
        )

        system += (
            "\n\nSpecial instructions:\n"
            "- If the caller asks to speak to the doctor, include [TRANSFER] at the start of your response\n"
            "- If you've successfully collected all booking details, include [BOOKED] at the start\n"
            "- Keep responses to 2-3 sentences max (this is a phone call)\n"
        )

        messages = [{"role": "system", "content": system}]
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({
                    "role": "user" if msg["from"] == "caller" else "assistant",
                    "content": msg["text"],
                })
        messages.append({"role": "user", "content": caller_speech})

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,  # Short for voice
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Voice AI failed: {e}")
            return self._fallback_voice_reply(caller_speech)

    def _fallback_voice_reply(self, speech: str) -> str:
        """Rule-based fallback for voice."""
        speech_lower = speech.lower()
        if any(w in speech_lower for w in ["appointment", "book", "slot"]):
            return "I'd love to help you book an appointment. What date and time works best for you?"
        elif any(w in speech_lower for w in ["doctor", "speak", "talk", "connect"]):
            return "[TRANSFER] Let me connect you with the doctor right away."
        elif any(w in speech_lower for w in ["emergency", "urgent", "pain"]):
            return "If this is an emergency, please call 108 immediately. For urgent concerns, let me connect you to the doctor. [TRANSFER]"
        elif any(w in speech_lower for w in ["price", "cost", "charge", "fee"]):
            return "Treatment costs depend on your specific needs. I'd recommend booking a consultation so the doctor can give you an accurate estimate. Shall I book one for you?"
        else:
            return "Thank you. Could you tell me more about how I can help you? I can book an appointment, share clinic information, or connect you with the doctor."

    def make_outbound_call(self, to: str, from_: str, webhook_url: str) -> Dict:
        """Make an outbound call (appointment reminder)."""
        if not self.is_active:
            return {"status": "demo_mode", "message": "Twilio not configured"}

        try:
            call = self.twilio_client.calls.create(
                to=to,
                from_=from_,
                url=f"{webhook_url}/api/v1/calls/outbound-handler",
                method="POST",
                status_callback=f"{webhook_url}/api/v1/calls/status",
                status_callback_method="POST",
                record=True,
            )
            return {"status": "initiated", "call_sid": call.sid}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_call_recordings(self, call_sid: str) -> list:
        """Get recordings for a call."""
        if not self.is_active:
            return []

        try:
            recordings = self.twilio_client.recordings.list(call_sid=call_sid)
            return [{"sid": r.sid, "duration": r.duration, "url": r.uri} for r in recordings]
        except Exception as e:
            logger.error(f"Failed to get recordings: {e}")
            return []


twilio_voice_ai = TwilioVoiceAI()
