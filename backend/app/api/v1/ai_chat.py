"""AI Chat Assistant — the doctor's command center inside the dashboard.

Doctors and front desk staff can:
- Ask about their data: "How many appointments do I have today?"
- Get reports: "Show me this week's revenue breakdown"
- Request changes: "Cancel Rahul's appointment tomorrow"
- Get insights: "Which treatment brings the most revenue?"
- Ask for help: "How do I connect WhatsApp?"

The AI has access to the doctor's real data:
- Campaign metrics (spend, clicks, conversions)
- Appointment data (bookings, attendance, revenue)
- Patient information (names, treatments, history)
- Integration status (what's connected, what's not)
"""

import logging
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_doctor
from app.core.config import settings
from app.db.session import get_db
from app.models.conversation import Appointment, AppointmentStatus
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-chat", tags=["ai-chat"])


class ChatMessage(BaseModel):
    message: str
    conversation_id: str | None = None  # For multi-turn conversations


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str | None = None
    data: dict | None = None  # Structured data if the reply includes numbers/tables
    actions: list[dict] | None = None  # Suggested actions the UI can render as buttons


@router.post("/message")
async def chat_message(
    body: ChatMessage,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Process a chat message from the doctor/front desk.

    Strategy:
    1. Gather clinic context (appointments, campaigns, integrations)
    2. Build a system prompt with the doctor's real data
    3. Send to Claude API for natural language response
    4. If Claude API not configured, use rule-based responses
    """
    # Medical advice guardrail — detect patient health questions routed through doctor's chat
    medical_keywords = ["bleeding", "pain", "swelling", "infection", "fever", "medicine", "tablet",
                        "dose", "dosage", "antibiotic", "painkiller", "remedy", "symptom", "diagnos"]
    msg_lower = body.message.lower()
    if any(kw in msg_lower for kw in medical_keywords) and any(
        q in msg_lower for q in ["what should", "how to treat", "which medicine", "is it normal", "home remedy"]
    ):
        return {
            "reply": "I'm your clinic management assistant — I help with appointments, ads, and analytics. For medical questions, please consult with the doctor directly. I can help you schedule an appointment if a patient needs to be seen.",
            "data": None,
        }

    # Gather clinic data context
    context = await _gather_clinic_context(doctor, db)

    # Try Claude API first, fall back to rule-based
    if settings.CLAUDE_API_KEY:
        reply_data = await _claude_response(body.message, context, doctor)
    else:
        reply_data = _rule_based_response(body.message, context, doctor)

    return reply_data


@router.get("/suggestions")
async def get_suggestions(
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Return contextual chat suggestions based on the doctor's current state."""
    context = await _gather_clinic_context(doctor, db)

    suggestions = []

    # Time-based suggestions
    if context["today_appointments"] == 0:
        suggestions.append({"text": "Any appointments today?", "icon": "calendar"})
    else:
        suggestions.append({"text": f"Show today's {context['today_appointments']} appointments", "icon": "calendar"})

    # Campaign suggestions
    if context["active_campaigns"] > 0:
        suggestions.append({"text": "How are my ads performing?", "icon": "trending-up"})
    else:
        suggestions.append({"text": "How do I start running ads?", "icon": "megaphone"})

    # Revenue suggestions
    if context["total_revenue"] > 0:
        suggestions.append({"text": "Show revenue breakdown by treatment", "icon": "indian-rupee"})
    else:
        suggestions.append({"text": "How do I track revenue?", "icon": "indian-rupee"})

    # Appointment suggestions
    if context["upcoming_appointments"] > 0:
        suggestions.append({"text": f"Who's coming in this week? ({context['upcoming_appointments']} booked)", "icon": "users"})

    # Integration suggestions
    if not context["whatsapp_connected"]:
        suggestions.append({"text": "How do I set up WhatsApp AI?", "icon": "message-circle"})

    # Always available
    suggestions.append({"text": "Generate a performance report", "icon": "file-text"})
    suggestions.append({"text": "What can you help me with?", "icon": "help-circle"})

    return {"suggestions": suggestions[:6]}


# ─── Context Gathering ───

async def _gather_clinic_context(doctor: Doctor, db: AsyncSession) -> dict:
    """Pull the doctor's current data for the AI to reference."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Today's appointments
    today_result = await db.execute(
        select(func.count()).select_from(Appointment).where(
            and_(Appointment.doctor_id == doctor.id, Appointment.appointment_date == today)
        )
    )
    today_count = today_result.scalar() or 0

    # This week's appointments
    week_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= week_start,
                Appointment.appointment_date <= today + timedelta(days=(6 - today.weekday())),
            )
        )
    )
    week_appts = week_result.scalars().all()

    # This month's stats
    month_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= month_start,
            )
        )
    )
    month_appts = month_result.scalars().all()

    # Revenue
    total_revenue = sum(a.revenue_amount or 0 for a in month_appts)
    attended = sum(1 for a in month_appts if a.status == AppointmentStatus.ATTENDED)
    no_shows = sum(1 for a in month_appts if a.status == AppointmentStatus.NO_SHOW)
    upcoming = sum(1 for a in week_appts if a.status in (AppointmentStatus.CONFIRMED, AppointmentStatus.REMINDED) and a.appointment_date >= today)

    # Treatment breakdown
    treatments: dict[str, int] = {}
    for a in month_appts:
        treatments[a.treatment] = treatments.get(a.treatment, 0) + 1

    # Campaign data
    try:
        from app.services.google_ads_service import google_ads_service
        campaign_data = await google_ads_service.get_campaign_overview(doctor)
    except Exception:
        campaign_data = {"total_campaigns": 0, "active_campaigns": 0, "total_spend": 0, "total_clicks": 0, "total_conversions": 0}

    return {
        "doctor_name": doctor.full_name,
        "clinic_name": doctor.clinic_name or "Your clinic",
        "specialty": doctor.specialty.value if doctor.specialty else "General",
        "city": doctor.city or "",
        "today_appointments": today_count,
        "upcoming_appointments": upcoming,
        "this_week_total": len(week_appts),
        "this_month_total": len(month_appts),
        "attended": attended,
        "no_shows": no_shows,
        "total_revenue": total_revenue,
        "treatments": treatments,
        "active_campaigns": campaign_data.get("active_campaigns", 0),
        "total_spend": campaign_data.get("total_spend", 0),
        "total_clicks": campaign_data.get("total_clicks", 0),
        "total_conversions": campaign_data.get("total_conversions", 0),
        "google_ads_connected": doctor.google_ads_connected,
        "google_calendar_connected": doctor.google_calendar_connected,
        "whatsapp_connected": doctor.whatsapp_verified,
        "meta_ads_connected": doctor.meta_ads_connected,
    }


# ─── Claude API Response ───

async def _claude_response(message: str, context: dict, doctor: Doctor) -> dict:
    """Get a response from Claude API with the doctor's context."""
    import httpx

    system_prompt = f"""You are PatientPlex AI Assistant — the AI helper for {context['doctor_name']} at {context['clinic_name']} ({context['specialty']}, {context['city']}).

You help doctors and front desk staff manage their clinic. You have access to their real data:

CURRENT DATA (as of today):
- Today's appointments: {context['today_appointments']}
- Upcoming this week: {context['upcoming_appointments']}
- This month: {context['this_month_total']} total, {context['attended']} attended, {context['no_shows']} no-shows
- Revenue this month: ₹{context['total_revenue']:,.0f}
- Top treatments: {', '.join(f'{t}: {c}' for t, c in sorted(context['treatments'].items(), key=lambda x: -x[1])[:5]) if context['treatments'] else 'No data yet'}
- Active ad campaigns: {context['active_campaigns']}
- Ad spend this month: ₹{context['total_spend']:,.0f}
- Ad clicks: {context['total_clicks']}
- Enquiries from ads: {context['total_conversions']}

INTEGRATIONS:
- Google Ads: {'Connected ✅' if context['google_ads_connected'] else 'Not connected'}
- Google Calendar: {'Connected ✅' if context['google_calendar_connected'] else 'Not connected'}
- WhatsApp AI: {'Connected ✅' if context['whatsapp_connected'] else 'Not connected — needs Meta approval'}
- Meta Ads: {'Connected ✅' if context['meta_ads_connected'] else 'Not connected'}

RULES:
- Be concise and friendly. Use ₹ for currency. Speak like a helpful colleague, not a chatbot.
- If asked about data you have, give the numbers directly.
- If asked to do something (cancel appointment, change budget), explain the steps or say you'll help them do it from the dashboard.
- If asked about features that aren't ready yet (WhatsApp AI, Meta Ads), be honest — say what's needed to activate it.
- For reports, format data clearly with bullet points.
- Always end actionable messages with a clear next step.
- Respond in English. If the doctor writes in Hindi, respond in Hindi.
- Keep responses under 200 words unless a detailed report is requested.
"""

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": message}],
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            reply_text = data["content"][0]["text"]

            return {
                "reply": reply_text,
                "data": {
                    "today_appointments": context["today_appointments"],
                    "this_month_revenue": context["total_revenue"],
                    "active_campaigns": context["active_campaigns"],
                },
            }
    except Exception as exc:
        logger.error("Claude API error: %s", exc)
        # Fall back to rule-based
        return _rule_based_response(message, context, doctor)


# ─── Rule-Based Fallback ───

def _rule_based_response(message: str, context: dict, doctor: Doctor) -> dict:
    """Smart rule-based responses when Claude API isn't available."""
    msg = message.lower().strip()

    # Greetings
    if any(w in msg for w in ["hi", "hello", "hey", "namaste"]):
        return {
            "reply": f"Namaste, {doctor.full_name.split(' ')[0]}! 🙏 I'm your PatientPlex AI assistant. I can help you check appointments, review ad performance, generate reports, and more. What would you like to know?",
            "data": None,
        }

    # Help
    if any(w in msg for w in ["help", "what can you do", "features"]):
        return {
            "reply": "Here's what I can help with:\n\n"
                     "📅 **Appointments** — \"How many appointments today?\" \"Who's coming this week?\"\n"
                     "📊 **Ad Performance** — \"How are my ads doing?\" \"What's my cost per lead?\"\n"
                     "💰 **Revenue** — \"Show revenue this month\" \"Which treatment earns most?\"\n"
                     "🔧 **Setup** — \"How do I connect WhatsApp?\" \"Set up Google Calendar\"\n"
                     "📋 **Reports** — \"Generate weekly report\" \"Performance summary\"\n\n"
                     "Just ask in English or Hindi!",
            "data": None,
        }

    # Today's appointments
    if "today" in msg and ("appointment" in msg or "patient" in msg or "schedule" in msg):
        count = context["today_appointments"]
        if count == 0:
            return {"reply": "No appointments scheduled for today. Would you like to log a walk-in or book one? Go to **Appointments** → **Log Appointment**.", "data": {"today_appointments": 0}}
        return {"reply": f"You have **{count} appointment{'s' if count > 1 else ''}** today. Check the full schedule in the **Appointments** page → Calendar view.", "data": {"today_appointments": count}}

    # This week
    if "week" in msg and ("appointment" in msg or "patient" in msg or "who" in msg or "schedule" in msg):
        return {
            "reply": f"This week: **{context['this_week_total']} appointments** booked, **{context['upcoming_appointments']} upcoming**.\n\nView the full week in **Appointments** → Calendar view (Week mode).",
            "data": {"this_week": context["this_week_total"], "upcoming": context["upcoming_appointments"]},
        }

    # Revenue
    if any(w in msg for w in ["revenue", "income", "earning", "money", "paisa", "kamai"]):
        rev = context["total_revenue"]
        treatments = context["treatments"]
        if rev > 0:
            top = sorted(treatments.items(), key=lambda x: -x[1])[:3]
            top_str = "\n".join(f"  • {t}: {c} appointments" for t, c in top)
            return {
                "reply": f"**Revenue this month: ₹{rev:,.0f}**\n\nFrom {context['this_month_total']} appointments ({context['attended']} attended).\n\nTop treatments:\n{top_str}\n\n💡 Tip: Mark appointments as 'Attended' and add the revenue amount to track this automatically.",
                "data": {"revenue": rev, "treatments": treatments},
            }
        return {"reply": "No revenue tracked yet this month. When you mark an appointment as **Attended**, add the treatment amount to start tracking revenue. Go to **Appointments** → click **Attended** on a completed visit.", "data": None}

    # Ad performance
    if any(w in msg for w in ["ad", "campaign", "ads", "google ads", "spend", "click", "marketing"]):
        if context["active_campaigns"] > 0:
            spend = context["total_spend"]
            clicks = context["total_clicks"]
            conversions = context["total_conversions"]
            cpc = round(spend / max(clicks, 1), 1)
            return {
                "reply": f"**Ad Performance (this month):**\n\n"
                         f"• Active campaigns: {context['active_campaigns']}\n"
                         f"• Total spend: ₹{spend:,.0f}\n"
                         f"• Clicks: {clicks:,}\n"
                         f"• Enquiries: {conversions}\n"
                         f"• Cost per click: ₹{cpc}\n"
                         f"{'• Cost per enquiry: ₹' + str(round(spend / max(conversions, 1))) if conversions > 0 else '• No enquiries tracked yet'}\n\n"
                         f"View details in **Campaigns** page.",
                "data": {"spend": spend, "clicks": clicks, "conversions": conversions},
            }
        return {"reply": "No active campaigns right now. Go to **Campaigns** → **Create Campaign** to launch Google Ads for your clinic. PatientPlex AI will optimize them automatically.", "data": None}

    # WhatsApp
    if any(w in msg for w in ["whatsapp", "receptionist", "chatbot"]):
        if context["whatsapp_connected"]:
            return {"reply": "Your WhatsApp AI receptionist is **active** ✅. It responds to patient messages automatically in Hindi and English, 24/7.", "data": None}
        return {
            "reply": "WhatsApp AI is not connected yet. Here's what's needed:\n\n"
                     "1. **Meta WhatsApp Business API** must be approved (submit at developers.facebook.com)\n"
                     "2. Once approved, go to **Settings** → **WhatsApp** → **Connect**\n"
                     "3. The AI receptionist will auto-respond to patients in Hindi/English\n\n"
                     "This is currently the #1 feature that will convert more patients.",
            "data": None,
        }

    # Report
    if any(w in msg for w in ["report", "summary", "overview", "performance"]):
        rev = context["total_revenue"]
        return {
            "reply": f"**📋 {context['clinic_name']} — Monthly Report**\n\n"
                     f"**Appointments:**\n"
                     f"• Total booked: {context['this_month_total']}\n"
                     f"• Attended: {context['attended']}\n"
                     f"• No-shows: {context['no_shows']}\n"
                     f"• Attendance rate: {round(context['attended'] / max(context['this_month_total'], 1) * 100)}%\n\n"
                     f"**Revenue:** ₹{rev:,.0f}\n\n"
                     f"**Ads:**\n"
                     f"• Spend: ₹{context['total_spend']:,.0f}\n"
                     f"• Clicks: {context['total_clicks']:,}\n"
                     f"• Enquiries: {context['total_conversions']}\n\n"
                     f"**Integrations:** Google Ads {'✅' if context['google_ads_connected'] else '❌'} · "
                     f"Calendar {'✅' if context['google_calendar_connected'] else '❌'} · "
                     f"WhatsApp {'✅' if context['whatsapp_connected'] else '❌'} · "
                     f"Meta Ads {'✅' if context['meta_ads_connected'] else '❌'}",
            "data": {
                "appointments": context["this_month_total"],
                "revenue": rev,
                "spend": context["total_spend"],
            },
        }

    # Cancel / reschedule
    if any(w in msg for w in ["cancel", "reschedule", "postpone", "move"]):
        return {"reply": "To cancel or reschedule an appointment:\n\n1. Go to **Appointments** page\n2. Find the appointment\n3. Click **Cancel** or change the date/time\n\nI can't cancel appointments directly yet — this ensures no accidental cancellations. This feature is coming soon!", "data": None}

    # Fallback
    return {
        "reply": f"I'm here to help! Try asking me about:\n\n"
                 f"• \"How many appointments today?\"\n"
                 f"• \"How are my ads performing?\"\n"
                 f"• \"Show revenue this month\"\n"
                 f"• \"Generate a report\"\n"
                 f"• \"How do I connect WhatsApp?\"\n\n"
                 f"Or ask anything about your clinic — I have access to your real data.",
        "data": None,
    }
