"""
PatientPlex Conversion Signals Engine

Tracks signals across all platforms, scores leads, and sends
enhanced conversion data back to ad platforms for optimization.

Platforms: Google Ads, Meta/Instagram, TikTok, LinkedIn, WhatsApp
Signals: page visits, form fills, WhatsApp messages, calls, bookings,
         no-shows, revenue, treatment type, time on site, device, location
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    # Awareness signals
    AD_IMPRESSION = "ad_impression"
    AD_CLICK = "ad_click"
    PAGE_VIEW = "page_view"
    TIME_ON_SITE = "time_on_site"

    # Interest signals
    TREATMENT_PAGE_VIEW = "treatment_page_view"
    PRICING_PAGE_VIEW = "pricing_page_view"
    MULTIPLE_PAGE_VIEWS = "multiple_page_views"
    RETURN_VISIT = "return_visit"

    # Intent signals (high value)
    WHATSAPP_MESSAGE = "whatsapp_message"
    PHONE_CALL = "phone_call"
    FORM_SUBMISSION = "form_submission"
    BOOKING_STARTED = "booking_started"

    # Conversion signals
    APPOINTMENT_BOOKED = "appointment_booked"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_ATTENDED = "appointment_attended"
    APPOINTMENT_NO_SHOW = "appointment_no_show"

    # Revenue signals
    TREATMENT_COMPLETED = "treatment_completed"
    PAYMENT_RECEIVED = "payment_received"
    FOLLOW_UP_BOOKED = "follow_up_booked"
    REFERRAL_MADE = "referral_made"


class Platform(str, Enum):
    GOOGLE_ADS = "google_ads"
    META = "meta"  # Facebook + Instagram
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    ORGANIC = "organic"
    DIRECT = "direct"


# Signal weights for lead scoring
SIGNAL_WEIGHTS: Dict[SignalType, int] = {
    SignalType.AD_CLICK: 5,
    SignalType.PAGE_VIEW: 2,
    SignalType.TIME_ON_SITE: 3,
    SignalType.TREATMENT_PAGE_VIEW: 10,
    SignalType.PRICING_PAGE_VIEW: 15,
    SignalType.MULTIPLE_PAGE_VIEWS: 8,
    SignalType.RETURN_VISIT: 20,
    SignalType.WHATSAPP_MESSAGE: 30,
    SignalType.PHONE_CALL: 35,
    SignalType.FORM_SUBMISSION: 40,
    SignalType.BOOKING_STARTED: 50,
    SignalType.APPOINTMENT_BOOKED: 80,
    SignalType.APPOINTMENT_CONFIRMED: 85,
    SignalType.APPOINTMENT_ATTENDED: 100,
    SignalType.TREATMENT_COMPLETED: 100,
    SignalType.PAYMENT_RECEIVED: 100,
    SignalType.FOLLOW_UP_BOOKED: 90,
    SignalType.REFERRAL_MADE: 95,
}


@dataclass
class Signal:
    signal_type: SignalType
    platform: Platform
    timestamp: str
    patient_id: Optional[str] = None
    clinic_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    # For enhanced conversions
    hashed_email: Optional[str] = None
    hashed_phone: Optional[str] = None
    gclid: Optional[str] = None  # Google click ID
    fbclid: Optional[str] = None  # Facebook click ID
    ttclid: Optional[str] = None  # TikTok click ID
    value_inr: float = 0.0


@dataclass
class LeadScore:
    patient_id: str
    score: float  # 0-100
    signals_count: int
    conversion_probability: float  # 0-1
    stage: str  # awareness, interest, intent, booking, converted, retained
    top_signals: List[str]
    recommended_action: str
    last_signal_at: str


class ConversionSignalsEngine:
    """Core engine that processes signals and manages enhanced conversions."""

    def __init__(self):
        self.signals: Dict[str, List[Signal]] = {}  # patient_id -> signals
        self.clinic_signals: Dict[str, List[Signal]] = {}  # clinic_id -> signals

    # === SIGNAL INGESTION ===

    def record_signal(self, signal: Signal) -> Dict:
        """Record a conversion signal from any platform."""
        pid = signal.patient_id or "anonymous"

        if pid not in self.signals:
            self.signals[pid] = []
        self.signals[pid].append(signal)

        if signal.clinic_id:
            if signal.clinic_id not in self.clinic_signals:
                self.clinic_signals[signal.clinic_id] = []
            self.clinic_signals[signal.clinic_id].append(signal)

        # Calculate updated lead score
        lead_score = self.score_lead(pid)

        # Check if we should send enhanced conversion to platforms
        enhanced_conversion = None
        if signal.signal_type in [
            SignalType.APPOINTMENT_BOOKED,
            SignalType.PAYMENT_RECEIVED,
            SignalType.TREATMENT_COMPLETED,
        ]:
            enhanced_conversion = self._prepare_enhanced_conversion(signal)

        return {
            "recorded": True,
            "patient_id": pid,
            "signal_type": signal.signal_type.value,
            "lead_score": lead_score.score,
            "stage": lead_score.stage,
            "enhanced_conversion": enhanced_conversion,
        }

    # === LEAD SCORING ===

    def score_lead(self, patient_id: str) -> LeadScore:
        """Score a lead based on accumulated signals."""
        signals = self.signals.get(patient_id, [])

        if not signals:
            return LeadScore(
                patient_id=patient_id,
                score=0,
                signals_count=0,
                conversion_probability=0,
                stage="unknown",
                top_signals=[],
                recommended_action="No data",
                last_signal_at="",
            )

        # Calculate raw score
        raw_score = 0
        signal_types_seen: set = set()
        for s in signals:
            weight = SIGNAL_WEIGHTS.get(s.signal_type, 1)
            raw_score += weight
            signal_types_seen.add(s.signal_type)

        # Normalize to 0-100
        score = min(100.0, float(raw_score))

        # Recency bonus (signals in last 24h get 1.2x weight)
        recent_signals = [
            s for s in signals if self._is_recent(s.timestamp, hours=24)
        ]
        if recent_signals:
            score = min(100.0, score * 1.2)

        # Multi-platform bonus (engaged on 2+ platforms = higher intent)
        platforms = set(s.platform for s in signals)
        if len(platforms) >= 2:
            score = min(100.0, score * 1.15)

        # Determine stage
        stage = self._determine_stage(signal_types_seen, score)

        # Conversion probability
        conv_prob = self._calculate_conversion_probability(score, signal_types_seen)

        # Top signals
        top = sorted(
            signals,
            key=lambda s: SIGNAL_WEIGHTS.get(s.signal_type, 0),
            reverse=True,
        )[:3]
        top_signals = [
            f"{s.signal_type.value} via {s.platform.value}" for s in top
        ]

        # Recommended action
        action = self._recommend_action(stage, signal_types_seen, recent_signals)

        last_at = max(s.timestamp for s in signals) if signals else ""

        return LeadScore(
            patient_id=patient_id,
            score=round(score, 1),
            signals_count=len(signals),
            conversion_probability=round(conv_prob, 3),
            stage=stage,
            top_signals=top_signals,
            recommended_action=action,
            last_signal_at=last_at,
        )

    def get_hot_leads(
        self, clinic_id: str, min_score: float = 50
    ) -> List[LeadScore]:
        """Get leads most likely to convert for a clinic."""
        clinic_patients: set = set()
        for s in self.clinic_signals.get(clinic_id, []):
            if s.patient_id:
                clinic_patients.add(s.patient_id)

        leads = []
        for pid in clinic_patients:
            lead = self.score_lead(pid)
            if lead.score >= min_score:
                leads.append(lead)

        return sorted(leads, key=lambda l: l.score, reverse=True)

    # === ENHANCED CONVERSIONS ===

    def _prepare_enhanced_conversion(self, signal: Signal) -> Dict:
        """Prepare enhanced conversion data for ad platforms."""
        conversions: Dict = {}

        # Google Ads Enhanced Conversions
        if signal.gclid or signal.hashed_email:
            gc: Dict = {
                "conversion_action": self._map_to_google_conversion(
                    signal.signal_type
                ),
                "gclid": signal.gclid,
                "conversion_date_time": signal.timestamp,
                "conversion_value": signal.value_inr,
                "currency_code": "INR",
                "user_identifiers": {},
            }
            if signal.hashed_email:
                gc["user_identifiers"]["hashed_email"] = signal.hashed_email
            if signal.hashed_phone:
                gc["user_identifiers"][
                    "hashed_phone_number"
                ] = signal.hashed_phone
            conversions["google_ads"] = gc

        # Meta/Instagram Conversions API (CAPI)
        if signal.fbclid or signal.hashed_email:
            mc: Dict = {
                "event_name": self._map_to_meta_event(signal.signal_type),
                "event_time": signal.timestamp,
                "event_source_url": signal.metadata.get("source_url", ""),
                "action_source": "website",
                "user_data": {},
                "custom_data": {
                    "currency": "INR",
                    "value": signal.value_inr,
                    "content_name": signal.metadata.get("treatment", ""),
                },
            }
            if signal.hashed_email:
                mc["user_data"]["em"] = [signal.hashed_email]
            if signal.hashed_phone:
                mc["user_data"]["ph"] = [signal.hashed_phone]
            if signal.fbclid:
                mc["user_data"]["fbc"] = signal.fbclid
            conversions["meta_capi"] = mc

        # TikTok Events API
        if signal.ttclid or signal.hashed_email:
            tt: Dict = {
                "event": self._map_to_tiktok_event(signal.signal_type),
                "event_time": signal.timestamp,
                "user": {},
                "properties": {
                    "currency": "INR",
                    "value": signal.value_inr,
                    "content_type": "product",
                    "description": signal.metadata.get("treatment", ""),
                },
            }
            if signal.hashed_email:
                tt["user"]["email"] = signal.hashed_email
            if signal.hashed_phone:
                tt["user"]["phone_number"] = signal.hashed_phone
            if signal.ttclid:
                tt["user"]["ttclid"] = signal.ttclid
            conversions["tiktok"] = tt

        # LinkedIn Conversions API
        if signal.hashed_email:
            conversions["linkedin"] = {
                "conversion": self._map_to_linkedin_conversion(
                    signal.signal_type
                ),
                "conversionHappenedAt": signal.timestamp,
                "conversionValue": {
                    "currencyCode": "INR",
                    "amount": str(signal.value_inr),
                },
                "user": {
                    "userIds": [
                        {
                            "idType": "SHA256_EMAIL",
                            "idValue": signal.hashed_email,
                        }
                    ]
                },
            }

        return conversions

    # === PLATFORM EVENT MAPPINGS ===

    def _map_to_google_conversion(self, signal_type: SignalType) -> str:
        mapping = {
            SignalType.APPOINTMENT_BOOKED: "appointment_booked",
            SignalType.APPOINTMENT_ATTENDED: "appointment_attended",
            SignalType.TREATMENT_COMPLETED: "purchase",
            SignalType.PAYMENT_RECEIVED: "purchase",
            SignalType.FORM_SUBMISSION: "submit_lead_form",
            SignalType.PHONE_CALL: "phone_call_lead",
            SignalType.WHATSAPP_MESSAGE: "contact",
        }
        return mapping.get(signal_type, "other")

    def _map_to_meta_event(self, signal_type: SignalType) -> str:
        mapping = {
            SignalType.APPOINTMENT_BOOKED: "Schedule",
            SignalType.TREATMENT_COMPLETED: "Purchase",
            SignalType.PAYMENT_RECEIVED: "Purchase",
            SignalType.FORM_SUBMISSION: "Lead",
            SignalType.PHONE_CALL: "Contact",
            SignalType.WHATSAPP_MESSAGE: "Contact",
            SignalType.BOOKING_STARTED: "InitiateCheckout",
        }
        return mapping.get(signal_type, "CustomEvent")

    def _map_to_tiktok_event(self, signal_type: SignalType) -> str:
        mapping = {
            SignalType.APPOINTMENT_BOOKED: "CompletePayment",
            SignalType.TREATMENT_COMPLETED: "CompletePayment",
            SignalType.FORM_SUBMISSION: "SubmitForm",
            SignalType.PHONE_CALL: "Contact",
            SignalType.BOOKING_STARTED: "InitiateCheckout",
        }
        return mapping.get(signal_type, "CustomEvent")

    def _map_to_linkedin_conversion(self, signal_type: SignalType) -> str:
        mapping = {
            SignalType.APPOINTMENT_BOOKED: "BOOK_APPOINTMENT",
            SignalType.FORM_SUBMISSION: "SUBMIT_LEAD_FORM",
            SignalType.PHONE_CALL: "PHONE_CALL",
        }
        return mapping.get(signal_type, "OTHER")

    # === HELPER METHODS ===

    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        try:
            t = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return (datetime.now(t.tzinfo) - t) < timedelta(hours=hours)
        except Exception:
            return False

    def _determine_stage(self, signals_seen: set, score: float) -> str:
        if any(
            s in signals_seen
            for s in [SignalType.TREATMENT_COMPLETED, SignalType.PAYMENT_RECEIVED]
        ):
            return "converted"
        if any(
            s in signals_seen
            for s in [SignalType.FOLLOW_UP_BOOKED, SignalType.REFERRAL_MADE]
        ):
            return "retained"
        if any(s in signals_seen for s in [SignalType.APPOINTMENT_ATTENDED]):
            return "attended"
        if any(
            s in signals_seen
            for s in [
                SignalType.APPOINTMENT_BOOKED,
                SignalType.APPOINTMENT_CONFIRMED,
            ]
        ):
            return "booked"
        if any(
            s in signals_seen
            for s in [
                SignalType.WHATSAPP_MESSAGE,
                SignalType.PHONE_CALL,
                SignalType.FORM_SUBMISSION,
                SignalType.BOOKING_STARTED,
            ]
        ):
            return "intent"
        if any(
            s in signals_seen
            for s in [
                SignalType.TREATMENT_PAGE_VIEW,
                SignalType.PRICING_PAGE_VIEW,
                SignalType.RETURN_VISIT,
            ]
        ):
            return "interest"
        return "awareness"

    def _calculate_conversion_probability(
        self, score: float, signals_seen: set
    ) -> float:
        base = score / 100
        if SignalType.WHATSAPP_MESSAGE in signals_seen:
            base = min(1.0, base * 1.3)
        if SignalType.PHONE_CALL in signals_seen:
            base = min(1.0, base * 1.4)
        if SignalType.BOOKING_STARTED in signals_seen:
            base = min(1.0, base * 1.5)
        return min(1.0, base)

    def _recommend_action(
        self, stage: str, signals: set, recent: list
    ) -> str:
        actions = {
            "awareness": "Send targeted ad with clinic-specific offer",
            "interest": "Retarget with treatment-specific WhatsApp message",
            "intent": "Immediate follow-up — this lead is hot. Call or WhatsApp within 5 min",
            "booked": "Send appointment confirmation + reminder. Reduce no-show risk",
            "attended": "Follow up for treatment feedback + ask for Google review",
            "converted": "Send follow-up care instructions + book next appointment",
            "retained": "Ask for referral + upsell related treatments",
        }
        return actions.get(stage, "Monitor and re-engage")

    # === CLINIC ANALYTICS ===

    def get_funnel_metrics(self, clinic_id: str) -> Dict:
        """Full funnel metrics for a clinic."""
        signals = self.clinic_signals.get(clinic_id, [])

        stages = {
            "impressions": 0,
            "clicks": 0,
            "page_views": 0,
            "enquiries": 0,
            "bookings": 0,
            "attended": 0,
            "no_shows": 0,
            "treatments": 0,
            "revenue_inr": 0.0,
        }

        for s in signals:
            if s.signal_type == SignalType.AD_IMPRESSION:
                stages["impressions"] += 1
            elif s.signal_type == SignalType.AD_CLICK:
                stages["clicks"] += 1
            elif s.signal_type == SignalType.PAGE_VIEW:
                stages["page_views"] += 1
            elif s.signal_type in [
                SignalType.WHATSAPP_MESSAGE,
                SignalType.PHONE_CALL,
                SignalType.FORM_SUBMISSION,
            ]:
                stages["enquiries"] += 1
            elif s.signal_type == SignalType.APPOINTMENT_BOOKED:
                stages["bookings"] += 1
            elif s.signal_type == SignalType.APPOINTMENT_ATTENDED:
                stages["attended"] += 1
            elif s.signal_type == SignalType.APPOINTMENT_NO_SHOW:
                stages["no_shows"] += 1
            elif s.signal_type in [
                SignalType.TREATMENT_COMPLETED,
                SignalType.PAYMENT_RECEIVED,
            ]:
                stages["treatments"] += 1
                stages["revenue_inr"] += s.value_inr

        # Calculate rates
        metrics = {**stages}
        metrics["ctr"] = round(
            stages["clicks"] / max(stages["impressions"], 1) * 100, 2
        )
        metrics["enquiry_rate"] = round(
            stages["enquiries"] / max(stages["clicks"], 1) * 100, 2
        )
        metrics["booking_rate"] = round(
            stages["bookings"] / max(stages["enquiries"], 1) * 100, 2
        )
        metrics["show_rate"] = round(
            stages["attended"] / max(stages["bookings"], 1) * 100, 2
        )
        metrics["no_show_rate"] = round(
            stages["no_shows"] / max(stages["bookings"], 1) * 100, 2
        )
        metrics["treatment_rate"] = round(
            stages["treatments"] / max(stages["attended"], 1) * 100, 2
        )

        # Cost metrics
        total_spend = sum(
            s.metadata.get("cost_inr", 0)
            for s in signals
            if s.signal_type == SignalType.AD_CLICK
        )
        metrics["total_ad_spend_inr"] = round(total_spend, 2)
        metrics["cost_per_click_inr"] = round(
            total_spend / max(stages["clicks"], 1), 2
        )
        metrics["cost_per_enquiry_inr"] = round(
            total_spend / max(stages["enquiries"], 1), 2
        )
        metrics["cost_per_booking_inr"] = round(
            total_spend / max(stages["bookings"], 1), 2
        )
        metrics["cost_per_attended_inr"] = round(
            total_spend / max(stages["attended"], 1), 2
        )
        metrics["roas"] = round(
            stages["revenue_inr"] / max(total_spend, 1), 2
        )

        return metrics

    @staticmethod
    def hash_pii(value: str) -> str:
        """SHA256 hash PII for enhanced conversions (industry standard)."""
        return hashlib.sha256(value.strip().lower().encode()).hexdigest()
