"""
Compliance API routes — validate ads, messages, and data handling
against NMC, DPDP, and ASCI rules before going live.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.services.compliance_checker import ComplianceChecker

router = APIRouter(prefix="/compliance", tags=["Compliance"])

checker = ComplianceChecker()


# === Request Models ===

class AdCopyCheckRequest(BaseModel):
    headline: str = Field(..., min_length=1, max_length=300, description="Ad headline text")
    description: str = Field(..., min_length=1, max_length=1000, description="Ad description text")
    treatment: str = Field("", description="Treatment being advertised (optional)")
    clinic_name: str = Field("", description="Clinic name (optional)")


class MessageCheckRequest(BaseModel):
    message_text: str = Field(..., min_length=1, max_length=5000)
    message_type: str = Field("marketing", description="marketing | transactional | reminder")
    has_patient_optin: bool = Field(False, description="Has the patient opted in to marketing messages?")
    is_existing_patient: bool = Field(False, description="Is this an existing patient of the clinic?")


class DataConsentCheckRequest(BaseModel):
    has_consent: bool = False
    consent_purpose: str = ""
    data_usage: str = ""
    is_encrypted: bool = False
    has_opt_out: bool = False
    data_fields: List[str] = Field(default_factory=list)
    is_minor: bool = False
    has_parental_consent: bool = False


# === Endpoints ===

@router.post("/check-ad-copy")
async def check_ad_copy(req: AdCopyCheckRequest):
    """
    Validate ad copy against NMC Oct 2026 ethical advertising guidelines,
    ASCI standards, and DPDP Act 2023 rules.

    Returns compliance score (0-100), list of violations, warnings,
    suggestions, and auto-corrected text if non-compliant.
    """
    result = checker.check_ad_copy(
        headline=req.headline,
        description=req.description,
        treatment=req.treatment,
        clinic_name=req.clinic_name,
    )
    return {
        "compliant": result.compliant,
        "score": result.score,
        "violations": [
            {
                "rule_id": v.rule_id,
                "category": v.category.value,
                "severity": v.severity.value,
                "message": v.message,
                "matched_text": v.matched_text,
                "suggestion": v.suggestion,
            }
            for v in result.violations
        ],
        "warnings": [
            {
                "rule_id": w.rule_id,
                "category": w.category.value,
                "severity": w.severity.value,
                "message": w.message,
                "matched_text": w.matched_text,
                "suggestion": w.suggestion,
            }
            for w in result.warnings
        ],
        "suggestions": result.suggestions,
        "corrected_text": result.corrected_text,
        "checked_at": result.checked_at,
    }


@router.post("/check-message")
async def check_message(req: MessageCheckRequest):
    """
    Validate a WhatsApp/SMS message against DPDP opt-in rules,
    NMC health claim restrictions, and messaging best practices.
    """
    result = checker.check_message(
        message_text=req.message_text,
        message_type=req.message_type,
        has_patient_optin=req.has_patient_optin,
        is_existing_patient=req.is_existing_patient,
    )
    return {
        "compliant": result.compliant,
        "score": result.score,
        "violations": [
            {
                "rule_id": v.rule_id,
                "severity": v.severity.value,
                "message": v.message,
                "matched_text": v.matched_text,
                "suggestion": v.suggestion,
            }
            for v in result.violations
        ],
        "warnings": [
            {
                "rule_id": w.rule_id,
                "severity": w.severity.value,
                "message": w.message,
                "suggestion": w.suggestion,
            }
            for w in result.warnings
        ],
        "suggestions": result.suggestions,
        "checked_at": result.checked_at,
    }


@router.post("/check-data-consent")
async def check_data_consent(req: DataConsentCheckRequest):
    """
    Validate patient data handling against DPDP Act 2023 requirements.
    """
    result = checker.check_data_consent(req.model_dump())
    return {
        "compliant": result.compliant,
        "score": result.score,
        "violations": [
            {
                "rule_id": v.rule_id,
                "severity": v.severity.value,
                "message": v.message,
                "suggestion": v.suggestion,
            }
            for v in result.violations
        ],
        "warnings": [
            {
                "rule_id": w.rule_id,
                "severity": w.severity.value,
                "message": w.message,
                "suggestion": w.suggestion,
            }
            for w in result.warnings
        ],
        "suggestions": result.suggestions,
    }


@router.get("/rules")
async def get_rules():
    """
    List all active compliance rules organized by category
    (NMC, DPDP, ASCI, Messaging).
    """
    return checker.get_all_rules()
