"""API routes for the Conversion Signals Engine."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.services.signals_engine import (
    ConversionSignalsEngine,
    Signal,
    SignalType,
    Platform,
)

router = APIRouter(prefix="/signals", tags=["Conversion Signals"])

engine = ConversionSignalsEngine()


class SignalInput(BaseModel):
    signal_type: str
    platform: str
    patient_id: Optional[str] = None
    clinic_id: Optional[str] = None
    metadata: Dict = {}
    email: Optional[str] = None
    phone: Optional[str] = None
    gclid: Optional[str] = None
    fbclid: Optional[str] = None
    ttclid: Optional[str] = None
    value_inr: float = 0.0


@router.post("/record")
async def record_signal(data: SignalInput):
    """Record a conversion signal from any platform."""
    try:
        sig_type = SignalType(data.signal_type)
        plat = Platform(data.platform)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid signal_type or platform. Valid types: {[s.value for s in SignalType]}. Valid platforms: {[p.value for p in Platform]}",
        )

    from datetime import datetime

    signal = Signal(
        signal_type=sig_type,
        platform=plat,
        timestamp=datetime.utcnow().isoformat(),
        patient_id=data.patient_id,
        clinic_id=data.clinic_id,
        metadata=data.metadata,
        hashed_email=(
            ConversionSignalsEngine.hash_pii(data.email)
            if data.email
            else None
        ),
        hashed_phone=(
            ConversionSignalsEngine.hash_pii(data.phone)
            if data.phone
            else None
        ),
        gclid=data.gclid,
        fbclid=data.fbclid,
        ttclid=data.ttclid,
        value_inr=data.value_inr,
    )

    result = engine.record_signal(signal)
    return result


@router.get("/score/{patient_id}")
async def get_lead_score(patient_id: str):
    """Get lead score and conversion probability for a patient."""
    lead = engine.score_lead(patient_id)
    return {
        "patient_id": lead.patient_id,
        "score": lead.score,
        "signals_count": lead.signals_count,
        "conversion_probability": lead.conversion_probability,
        "stage": lead.stage,
        "top_signals": lead.top_signals,
        "recommended_action": lead.recommended_action,
        "last_signal_at": lead.last_signal_at,
    }


@router.get("/hot-leads/{clinic_id}")
async def get_hot_leads(clinic_id: str, min_score: float = 50):
    """Get leads most likely to convert for a clinic."""
    leads = engine.get_hot_leads(clinic_id, min_score)
    return {
        "clinic_id": clinic_id,
        "hot_leads": [
            {
                "patient_id": l.patient_id,
                "score": l.score,
                "conversion_probability": l.conversion_probability,
                "stage": l.stage,
                "recommended_action": l.recommended_action,
            }
            for l in leads
        ],
        "count": len(leads),
    }


@router.get("/funnel/{clinic_id}")
async def get_funnel_metrics(clinic_id: str):
    """Get full funnel metrics for a clinic."""
    return engine.get_funnel_metrics(clinic_id)


@router.get("/types")
async def list_signal_types():
    """List all available signal types and platforms."""
    return {
        "signal_types": [s.value for s in SignalType],
        "platforms": [p.value for p in Platform],
    }
