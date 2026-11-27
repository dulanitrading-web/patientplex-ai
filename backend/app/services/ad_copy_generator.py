"""AI-powered ad copy generation.

Generates Google Ads RSA headlines/descriptions and Meta ad copy
tailored to each doctor's specialty, services, and location.
"""

import json
import logging

from app.models.doctor import Doctor
from app.schemas.specialty import SPECIALTY_CONFIGS
from app.services.ai import AIProviderError, generate_text

logger = logging.getLogger(__name__)

GOOGLE_ADS_PROMPT = """Generate Google Responsive Search Ad (RSA) copy for a healthcare provider.

Doctor: {doctor_name}
Clinic: {clinic_name}
Specialty: {specialty}
Services: {services}
City: {city}

Requirements:
- 15 headlines (max 30 characters each)
- 4 descriptions (max 90 characters each)
- Must comply with Google Ads healthcare advertising policies
- NO cure claims, NO misleading promises, NO superlatives like "best" or "#1"
- Include location in some headlines
- Include call-to-action phrases: "Book Now", "Call Today", "Walk-ins Welcome"
- Use patient-centric language

Return as JSON with "headlines" (list of strings) and "descriptions" (list of strings)."""

META_ADS_PROMPT = """Generate Facebook/Instagram ad copy for a healthcare provider.

Doctor: {doctor_name}
Clinic: {clinic_name}
Specialty: {specialty}
Services: {services}
City: {city}

Requirements:
- 3 ad variations with different angles (awareness, trust, urgency)
- Each variation needs: "primary_text" (125 chars max), "headline" (40 chars), "description" (30 chars)
- Must comply with Meta healthcare advertising policies
- NO before/after claims, NO cure promises
- Warm, approachable tone

Return as JSON with "variations" (list of objects with primary_text, headline, description, angle)."""


async def generate_google_ad_copy(doctor: Doctor) -> dict:
    """Generate Google Ads RSA copy using the configured provider.

    Returns dict with 'headlines' and 'descriptions' lists.
    Falls back to template-based copy if API is unavailable.
    """
    services = ", ".join(doctor.services or ["General Consultation"])
    specialty = doctor.specialty.value if doctor.specialty else "General"

    prompt = GOOGLE_ADS_PROMPT.format(
        doctor_name=doctor.full_name,
        clinic_name=doctor.clinic_name or "Clinic",
        specialty=specialty,
        services=services,
        city=doctor.city or "",
    )

    result = await _generate_ad_copy(prompt)
    if result:
        return result

    # Fallback: template-based copy
    return _fallback_google_copy(doctor)


async def generate_meta_ad_copy(doctor: Doctor) -> dict:
    """Generate Meta (Facebook/Instagram) ad copy using the configured provider.

    Returns dict with 'variations' list.
    """
    services = ", ".join(doctor.services or ["General Consultation"])
    specialty = doctor.specialty.value if doctor.specialty else "General"

    prompt = META_ADS_PROMPT.format(
        doctor_name=doctor.full_name,
        clinic_name=doctor.clinic_name or "Clinic",
        specialty=specialty,
        services=services,
        city=doctor.city or "",
    )

    result = await _generate_ad_copy(prompt)
    if result:
        return result

    return _fallback_meta_copy(doctor)


async def _generate_ad_copy(prompt: str) -> dict | None:
    """Parse generated copy and fall back explicitly for campaign drafting."""
    try:
        text = await generate_text("Return only the requested JSON object.", prompt)
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].removesuffix("```").strip()
        result = json.loads(text)
        return result if isinstance(result, dict) else None
    except (AIProviderError, ValueError):
        logger.warning("Using template ad copy because generated copy is unavailable")
        return None


def _fallback_google_copy(doctor: Doctor) -> dict:
    """Template-based Google Ads copy when AI is unavailable."""
    name = doctor.full_name
    clinic = doctor.clinic_name or "Clinic"
    city = doctor.city or "Your City"
    specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Doctor"
    services = doctor.services or []
    first_service = services[0] if services else "Consultation"

    headlines = [
        f"{specialty} in {city}",
        f"{clinic} — Book Now",
        f"Dr. {name.split()[-1]} — {specialty}",
        f"{first_service} — {city}",
        "Book Appointment Today",
        f"Expert {specialty} Care",
        "Walk-ins Welcome",
        f"Top {specialty} — {city}",
        "Affordable Healthcare",
        "Same Day Appointments",
        f"{clinic} — {city}",
        "Call Now — Free Consult",
        f"Trusted {specialty}",
        "Modern Equipment & Care",
        "Family Healthcare",
    ]
    # Enforce 30-char limit
    headlines = [h[:30] for h in headlines]

    descriptions = [
        f"Visit {clinic} in {city}. Expert {specialty.lower()} care with modern facilities. Book your appointment online today."[:90],
        f"Dr. {name} offers {first_service.lower()} and more. Trusted by patients across {city}. Call or WhatsApp to book."[:90],
        f"Affordable {specialty.lower()} services. Same-day appointments available. Walk-ins welcome at {clinic}."[:90],
        f"Get quality healthcare at {clinic}. {len(services)}+ services offered. Book via WhatsApp — instant confirmation."[:90],
    ]

    return {"headlines": headlines, "descriptions": descriptions}


def _fallback_meta_copy(doctor: Doctor) -> dict:
    """Template-based Meta ad copy when AI is unavailable."""
    name = doctor.full_name
    clinic = doctor.clinic_name or "Clinic"
    city = doctor.city or "Your City"
    specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Doctor"

    return {
        "variations": [
            {
                "angle": "awareness",
                "primary_text": f"Looking for a trusted {specialty.lower()} in {city}? Visit {clinic} for expert care.",
                "headline": f"{specialty} — {city}",
                "description": "Book your visit today",
            },
            {
                "angle": "trust",
                "primary_text": f"Dr. {name} at {clinic} — experienced {specialty.lower()} care your family can trust.",
                "headline": f"Trusted by {city} Families",
                "description": "Expert healthcare near you",
            },
            {
                "angle": "urgency",
                "primary_text": f"Same-day appointments available at {clinic}! Don't wait — book your {specialty.lower()} visit now.",
                "headline": "Book Today — Limited Slots",
                "description": "WhatsApp to book instantly",
            },
        ]
    }
