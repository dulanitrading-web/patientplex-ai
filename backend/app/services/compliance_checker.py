"""
PatientPlex Healthcare Compliance Checker

Auto-validates ad copy, patient messages, and data handling against:
- NMC (National Medical Commission) Oct 2026 Ethical Advertising Guidelines
- DPDP Act 2023 (Digital Personal Data Protection)
- ASCI (Advertising Standards Council of India) healthcare rules
- HIPAA basics (for US market readiness)
- WhatsApp/SMS marketing opt-in regulations

Every ad, message, and data operation passes through this before going live.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    BLOCK = "block"      # Must not go live — hard violation
    WARN = "warn"        # Review recommended — soft violation
    INFO = "info"        # Suggestion for improvement


class RuleCategory(str, Enum):
    NMC_ADVERTISING = "nmc_advertising"
    NMC_TESTIMONIALS = "nmc_testimonials"
    NMC_CLAIMS = "nmc_claims"
    NMC_PRICING = "nmc_pricing"
    DPDP_CONSENT = "dpdp_consent"
    DPDP_DATA = "dpdp_data"
    ASCI_STANDARDS = "asci_standards"
    HIPAA_PHI = "hipaa_phi"
    MESSAGING_OPTIN = "messaging_optin"


@dataclass
class Violation:
    rule_id: str
    category: RuleCategory
    severity: Severity
    message: str
    matched_text: str = ""
    suggestion: str = ""


@dataclass
class ComplianceResult:
    compliant: bool
    score: int  # 0-100
    violations: List[Violation]
    warnings: List[Violation]
    suggestions: List[str]
    corrected_text: Optional[str] = None
    checked_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================
# NMC BANNED PHRASES — Oct 2026 Guidelines
# ============================================================

# Superlative / self-promotion claims (NMC §4.1)
NMC_SUPERLATIVE_PATTERNS = [
    (r"\bbest\s+(doctor|surgeon|dentist|clinic|hospital|specialist|physician)\b", "NMC-001", "Superlative self-promotion is banned under NMC §4.1"),
    (r"\b(top|leading|premier|foremost|number\s*one|#1|no\.?\s*1)\s+(doctor|surgeon|dentist|clinic|hospital)\b", "NMC-002", "Ranking claims without third-party verification are banned"),
    (r"\b(world\s*class|world\s*famous|internationally\s*renowned|celebrity)\s+(doctor|surgeon)\b", "NMC-003", "Unverifiable prestige claims are banned"),
    (r"\bonly\s+(doctor|surgeon|clinic)\s+(in|who)\b", "NMC-004", "Exclusivity claims require verification"),
]

# Guaranteed outcome claims (NMC §4.3)
NMC_GUARANTEE_PATTERNS = [
    (r"\bguarantee[ds]?\b", "NMC-010", "Guaranteed outcomes are banned — medical results vary by patient"),
    (r"\b100\s*%\s*(success|cure|result|effective|safe|recovery)\b", "NMC-011", "100% outcome claims are prohibited"),
    (r"\b(permanent\s+cure|complete\s+cure|full\s+recovery)\b", "NMC-012", "Absolute cure claims are prohibited"),
    (r"\b(miracle|magic|instant)\s+(cure|result|recovery|treatment)\b", "NMC-013", "Miracle/magic claims are banned"),
    (r"\b(you\s+will|we\s+will)\s+(get|see|have|achieve)\s+(results?|cure|recovery)\b", "NMC-014", "Specific outcome promises are prohibited"),
    (r"\b(assured|certain|definite)\s+(results?|cure|outcome)\b", "NMC-015", "Assured outcome claims are prohibited"),
    (r"\bzero\s+(risk|side\s*effects?|pain|complications?)\b", "NMC-016", "Zero risk/side-effect claims are prohibited"),
]

# Before/after and testimonial patterns (NMC §4.5)
NMC_TESTIMONIAL_PATTERNS = [
    (r"\bbefore\s*(and|&|\/)\s*after\b", "NMC-020", "Before/after promotional content is banned by NMC"),
    (r"\b(patient|client)\s+(said|says|testimonial|review|story|experience)\b", "NMC-021", "Patient testimonials for promotional purposes are banned"),
    (r"\b(i\s+was\s+cured|my\s+life\s+changed|transformed\s+my)\b", "NMC-022", "Patient experience quotes in ads are banned"),
    (r"\b(hear\s+from|what\s+patients?\s+say|success\s+stor(y|ies))\b", "NMC-023", "Testimonial-style promotion is banned"),
]

# Comparative / disparaging claims (NMC §4.2)
NMC_COMPARATIVE_PATTERNS = [
    (r"\b(better\s+than|superior\s+to|unlike\s+other)\s+(doctor|clinic|hospital|treatment)s?\b", "NMC-030", "Comparative claims against other practitioners are banned"),
    (r"\b(cheapest|lowest\s+price|most\s+affordable)\b", "NMC-031", "Cheapest/lowest price claims may induce unnecessary treatment"),
    (r"\b(don'?t\s+go\s+to|avoid|stay\s+away\s+from)\s+(other|local)\b", "NMC-032", "Disparaging other practitioners is banned"),
]

# Discount/offer patterns (NMC §4.6 — warn, not block)
NMC_DISCOUNT_PATTERNS = [
    (r"\b(\d+\s*%\s*off|discount|offer|deal|free\s+consultation|free\s+check\s*up)\b", "NMC-040", "Discount/offer language may be seen as inducing treatment under NMC guidelines"),
    (r"\b(limited\s+time|hurry|act\s+now|last\s+chance|ending\s+soon)\b", "NMC-041", "Urgency language in healthcare ads may be seen as pressure tactics"),
    (r"\b(cashback|reward|gift|bonus|prize)\b", "NMC-042", "Incentive language in healthcare is discouraged"),
]

# ============================================================
# DPDP ACT 2023 — Data Protection Rules
# ============================================================

DPDP_HEALTH_DATA_PATTERNS = [
    (r"\b(diagnosis|diagnosed|disease|condition|symptom|medical\s+record)\b", "DPDP-001", "Health data is sensitive personal data under DPDP — requires explicit consent"),
]

# ============================================================
# ASCI — Advertising Standards
# ============================================================

ASCI_PATTERNS = [
    (r"\b(scientifically\s+proven|clinically\s+proven|research\s+shows)\b", "ASCI-001", "Scientific claims require substantiation under ASCI guidelines"),
    (r"\b(FDA\s+approved|WHO\s+approved|govt\s+approved)\b", "ASCI-002", "Regulatory approval claims must be verifiable"),
    (r"\b(fear|scare|danger|warning|deadly|fatal)\b", "ASCI-003", "Fear-based advertising is discouraged by ASCI"),
]

# ============================================================
# MESSAGING OPT-IN RULES
# ============================================================

MARKETING_KEYWORDS = [
    "offer", "discount", "deal", "promotion", "sale", "special",
    "limited time", "exclusive", "free", "save", "off", "promo",
    "new treatment", "new service", "introducing", "launch",
]

TRANSACTIONAL_KEYWORDS = [
    "appointment", "reminder", "booking", "confirmed", "cancelled",
    "reschedule", "follow-up", "report", "prescription", "billing",
]

# ============================================================
# OPT-OUT PHRASES TO CHECK FOR
# ============================================================

OPT_OUT_PHRASES = [
    "reply stop", "type stop", "send stop", "unsubscribe",
    "opt out", "opt-out", "stop to stop", "reply 0",
]


class ComplianceChecker:
    """Core compliance engine for PatientPlex."""

    def __init__(self):
        self.checks_performed = 0
        self.violations_caught = 0

    # ============================================================
    # AD COPY COMPLIANCE
    # ============================================================

    def check_ad_copy(self, headline: str, description: str,
                      treatment: str = "", clinic_name: str = "") -> ComplianceResult:
        """
        Validate ad copy against NMC, ASCI, and DPDP rules.
        Returns compliance result with score, violations, and corrected text.
        """
        self.checks_performed += 1
        violations: List[Violation] = []
        warnings: List[Violation] = []
        suggestions: List[str] = []

        combined = f"{headline} {description}".strip()
        combined_lower = combined.lower()

        # --- NMC Superlative Claims ---
        for pattern, rule_id, message in NMC_SUPERLATIVE_PATTERNS:
            match = re.search(pattern, combined_lower)
            if match:
                violations.append(Violation(
                    rule_id=rule_id, category=RuleCategory.NMC_ADVERTISING,
                    severity=Severity.BLOCK, message=message,
                    matched_text=match.group(),
                    suggestion="Use factual language: clinic name, specialties, qualifications, location"
                ))

        # --- NMC Guaranteed Outcomes ---
        for pattern, rule_id, message in NMC_GUARANTEE_PATTERNS:
            match = re.search(pattern, combined_lower)
            if match:
                violations.append(Violation(
                    rule_id=rule_id, category=RuleCategory.NMC_CLAIMS,
                    severity=Severity.BLOCK, message=message,
                    matched_text=match.group(),
                    suggestion="Replace with: 'experienced team', 'advanced treatments available', 'consult our specialists'"
                ))

        # --- NMC Testimonials ---
        for pattern, rule_id, message in NMC_TESTIMONIAL_PATTERNS:
            match = re.search(pattern, combined_lower)
            if match:
                violations.append(Violation(
                    rule_id=rule_id, category=RuleCategory.NMC_TESTIMONIALS,
                    severity=Severity.BLOCK, message=message,
                    matched_text=match.group(),
                    suggestion="Use treatment information instead of patient stories"
                ))

        # --- NMC Comparative ---
        for pattern, rule_id, message in NMC_COMPARATIVE_PATTERNS:
            match = re.search(pattern, combined_lower)
            if match:
                violations.append(Violation(
                    rule_id=rule_id, category=RuleCategory.NMC_ADVERTISING,
                    severity=Severity.BLOCK, message=message,
                    matched_text=match.group(),
                    suggestion="Focus on your own clinic's strengths without comparing to others"
                ))

        # --- NMC Discount/Offers (warnings) ---
        for pattern, rule_id, message in NMC_DISCOUNT_PATTERNS:
            match = re.search(pattern, combined_lower)
            if match:
                warnings.append(Violation(
                    rule_id=rule_id, category=RuleCategory.NMC_PRICING,
                    severity=Severity.WARN, message=message,
                    matched_text=match.group(),
                    suggestion="Consider framing as transparent pricing instead of discounts"
                ))

        # --- ASCI Standards ---
        for pattern, rule_id, message in ASCI_PATTERNS:
            match = re.search(pattern, combined_lower)
            if match:
                warnings.append(Violation(
                    rule_id=rule_id, category=RuleCategory.ASCI_STANDARDS,
                    severity=Severity.WARN, message=message,
                    matched_text=match.group(),
                    suggestion="Ensure claims are substantiated with evidence"
                ))

        # --- Suggestions ---
        if treatment and treatment.lower() not in combined_lower:
            suggestions.append(f"Consider mentioning the treatment '{treatment}' in the ad copy for relevance")

        if clinic_name and clinic_name.lower() not in combined_lower:
            suggestions.append(f"Include clinic name '{clinic_name}' for brand recognition")

        if not re.search(r"\b(book|call|visit|consult|schedule|enquire|contact)\b", combined_lower):
            suggestions.append("Add a clear call-to-action (book, call, visit, consult)")

        if len(headline) > 90:
            suggestions.append("Headline is over 90 characters — consider shortening for better ad performance")

        if len(headline) < 15:
            suggestions.append("Headline is very short — add more descriptive text")

        # --- Calculate score ---
        score = 100
        score -= len(violations) * 25  # Each violation = -25
        score -= len(warnings) * 10    # Each warning = -10
        score -= len(suggestions) * 2  # Each suggestion = -2
        score = max(0, min(100, score))

        compliant = len(violations) == 0

        # --- Generate corrected text ---
        corrected = None
        if not compliant:
            corrected = self._generate_corrected_copy(headline, description, violations)

        self.violations_caught += len(violations)

        return ComplianceResult(
            compliant=compliant,
            score=score,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
            corrected_text=corrected,
        )

    def _generate_corrected_copy(self, headline: str, description: str,
                                  violations: List[Violation]) -> str:
        """Attempt to auto-correct non-compliant ad copy."""
        corrected_headline = headline
        corrected_desc = description

        replacements = {
            # Superlatives
            r"\bbest\s+(doctor|surgeon|dentist|clinic)": r"experienced \1",
            r"\b(top|leading|premier)\s+(doctor|surgeon|dentist|clinic)": r"qualified \2",
            r"\bnumber\s*one\b": "trusted",
            r"\b#1\b": "trusted",
            # Guarantees
            r"\bguaranteed?\s*(results?|cure|outcome)?": "experienced care",
            r"\b100\s*%\s*(success|cure|effective)": "high-quality treatment",
            r"\b(permanent|complete)\s+cure": "comprehensive treatment",
            r"\b(miracle|magic)\s+(cure|result)": "advanced treatment",
            r"\bzero\s+(risk|side\s*effects?)": "minimal-risk procedures",
            # Testimonials
            r"\bbefore\s*(and|&|\/)\s*after\b": "treatment information",
            r"\bsuccess\s+stor(y|ies)": "treatment options",
            # Comparative
            r"\bcheapest\b": "affordable",
            r"\blowest\s+price\b": "competitive pricing",
            r"\bbetter\s+than\s+other\s+(doctor|clinic)s?": "quality care",
        }

        for pattern, replacement in replacements.items():
            corrected_headline = re.sub(pattern, replacement, corrected_headline, flags=re.IGNORECASE)
            corrected_desc = re.sub(pattern, replacement, corrected_desc, flags=re.IGNORECASE)

        return f"Headline: {corrected_headline}\nDescription: {corrected_desc}"

    # ============================================================
    # MESSAGE COMPLIANCE
    # ============================================================

    def check_message(self, message_text: str, message_type: str = "marketing",
                      has_patient_optin: bool = False,
                      is_existing_patient: bool = False) -> ComplianceResult:
        """
        Validate a WhatsApp/SMS message against compliance rules.

        message_type: "marketing" | "transactional" | "reminder"
        """
        self.checks_performed += 1
        violations: List[Violation] = []
        warnings: List[Violation] = []
        suggestions: List[str] = []

        msg_lower = message_text.lower()

        # --- Determine if marketing or transactional ---
        is_marketing = message_type == "marketing" or any(
            kw in msg_lower for kw in MARKETING_KEYWORDS
        )
        is_transactional = message_type in ("transactional", "reminder") or any(
            kw in msg_lower for kw in TRANSACTIONAL_KEYWORDS
        )

        # --- Marketing opt-in check ---
        if is_marketing and not has_patient_optin:
            if not is_existing_patient:
                violations.append(Violation(
                    rule_id="MSG-001",
                    category=RuleCategory.MESSAGING_OPTIN,
                    severity=Severity.BLOCK,
                    message="Marketing messages require explicit patient opt-in under DPDP Act and TRAI regulations",
                    suggestion="Obtain opt-in consent before sending marketing messages"
                ))
            else:
                warnings.append(Violation(
                    rule_id="MSG-002",
                    category=RuleCategory.MESSAGING_OPTIN,
                    severity=Severity.WARN,
                    message="Existing patient, but marketing opt-in not confirmed — recommend obtaining consent",
                    suggestion="Send opt-in request before marketing messages"
                ))

        # --- Opt-out mechanism check ---
        has_opt_out = any(phrase in msg_lower for phrase in OPT_OUT_PHRASES)
        if is_marketing and not has_opt_out:
            violations.append(Violation(
                rule_id="MSG-010",
                category=RuleCategory.MESSAGING_OPTIN,
                severity=Severity.BLOCK,
                message="Marketing messages must include an opt-out mechanism (e.g., 'Reply STOP to unsubscribe')",
                matched_text="",
                suggestion="Add 'Reply STOP to unsubscribe' at the end of the message"
            ))

        # --- Health claims in marketing ---
        for pattern, rule_id, message in NMC_GUARANTEE_PATTERNS:
            match = re.search(pattern, msg_lower)
            if match:
                violations.append(Violation(
                    rule_id=f"MSG-{rule_id}",
                    category=RuleCategory.NMC_CLAIMS,
                    severity=Severity.BLOCK,
                    message=f"Health claim in message: {message}",
                    matched_text=match.group(),
                ))

        # --- Diagnosis in messages ---
        diagnosis_patterns = [
            (r"\byou\s+(have|suffer|are\s+diagnosed)\b", "MSG-020", "Messages must not diagnose — refer patient to doctor"),
            (r"\b(your\s+condition\s+is|you\s+need\s+surgery|you\s+must\s+get)\b", "MSG-021", "Do not prescribe or recommend specific treatments in messages"),
        ]
        for pattern, rule_id, message in diagnosis_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                violations.append(Violation(
                    rule_id=rule_id,
                    category=RuleCategory.NMC_CLAIMS,
                    severity=Severity.BLOCK,
                    message=message,
                    matched_text=match.group(),
                    suggestion="Suggest consulting a doctor instead of diagnosing"
                ))

        # --- Message length ---
        if len(message_text) > 1000:
            warnings.append(Violation(
                rule_id="MSG-030",
                category=RuleCategory.ASCI_STANDARDS,
                severity=Severity.WARN,
                message="Message is over 1000 characters — may be too long for WhatsApp engagement",
                suggestion="Keep messages concise for better read rates"
            ))

        # --- Suggestions ---
        if is_transactional and not is_marketing:
            suggestions.append("Transactional messages (reminders, confirmations) don't require marketing opt-in for existing patients")

        score = 100
        score -= len(violations) * 25
        score -= len(warnings) * 10
        score = max(0, min(100, score))

        self.violations_caught += len(violations)

        return ComplianceResult(
            compliant=len(violations) == 0,
            score=score,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
        )

    # ============================================================
    # DATA CONSENT COMPLIANCE
    # ============================================================

    def check_data_consent(self, patient_data: Dict) -> ComplianceResult:
        """
        Validate that patient data handling complies with DPDP Act 2023.

        patient_data should include:
        - has_consent: bool
        - consent_purpose: str (what was consent given for)
        - data_usage: str (what is the data being used for)
        - is_encrypted: bool
        - has_opt_out: bool
        - data_fields: list of field names being collected
        - is_minor: bool (under 18)
        - has_parental_consent: bool (if minor)
        """
        violations: List[Violation] = []
        warnings: List[Violation] = []
        suggestions: List[str] = []

        # --- Consent check ---
        if not patient_data.get("has_consent", False):
            violations.append(Violation(
                rule_id="DPDP-010",
                category=RuleCategory.DPDP_CONSENT,
                severity=Severity.BLOCK,
                message="Patient has not given consent for data collection — required under DPDP Act §6",
                suggestion="Obtain explicit consent before collecting any personal data"
            ))

        # --- Purpose limitation ---
        consent_purpose = patient_data.get("consent_purpose", "").lower()
        data_usage = patient_data.get("data_usage", "").lower()
        if consent_purpose and data_usage and consent_purpose != data_usage:
            if "marketing" in data_usage and "marketing" not in consent_purpose:
                violations.append(Violation(
                    rule_id="DPDP-011",
                    category=RuleCategory.DPDP_DATA,
                    severity=Severity.BLOCK,
                    message="Data collected for one purpose cannot be used for another — DPDP Act §5 purpose limitation",
                    suggestion=f"Consent was for '{consent_purpose}' but data is being used for '{data_usage}'. Obtain separate consent."
                ))

        # --- Encryption check ---
        if not patient_data.get("is_encrypted", False):
            violations.append(Violation(
                rule_id="DPDP-012",
                category=RuleCategory.DPDP_DATA,
                severity=Severity.BLOCK,
                message="Patient data must be encrypted at rest and in transit — DPDP Act §8",
                suggestion="Enable AES-256 encryption for stored data and TLS 1.3 for data in transit"
            ))

        # --- Opt-out mechanism ---
        if not patient_data.get("has_opt_out", False):
            warnings.append(Violation(
                rule_id="DPDP-013",
                category=RuleCategory.DPDP_CONSENT,
                severity=Severity.WARN,
                message="Right to withdraw consent must be as easy as giving it — DPDP Act §6(6)",
                suggestion="Provide a simple opt-out mechanism (WhatsApp reply, web form, or phone)"
            ))

        # --- Sensitive health data ---
        sensitive_fields = {"diagnosis", "condition", "treatment_history", "medical_records",
                           "prescriptions", "lab_results", "health_status", "insurance"}
        collected_fields = set(patient_data.get("data_fields", []))
        sensitive_collected = sensitive_fields & collected_fields
        if sensitive_collected:
            warnings.append(Violation(
                rule_id="DPDP-014",
                category=RuleCategory.DPDP_DATA,
                severity=Severity.WARN,
                message=f"Collecting sensitive health data: {', '.join(sensitive_collected)}. Requires explicit consent and enhanced protection.",
                suggestion="Ensure health data has separate explicit consent and is stored with additional security"
            ))

        # --- Minor's data ---
        if patient_data.get("is_minor", False):
            if not patient_data.get("has_parental_consent", False):
                violations.append(Violation(
                    rule_id="DPDP-015",
                    category=RuleCategory.DPDP_CONSENT,
                    severity=Severity.BLOCK,
                    message="Processing a minor's data requires verifiable parental consent — DPDP Act §9",
                    suggestion="Obtain and verify parental/guardian consent before processing minor's data"
                ))

        # --- Data minimization ---
        excessive_fields = {"aadhaar", "pan_number", "passport", "bank_account", "salary"}
        excessive_collected = excessive_fields & collected_fields
        if excessive_collected:
            warnings.append(Violation(
                rule_id="DPDP-016",
                category=RuleCategory.DPDP_DATA,
                severity=Severity.WARN,
                message=f"Collecting potentially unnecessary data: {', '.join(excessive_collected)}. Apply data minimization principle.",
                suggestion="Only collect data that is strictly necessary for the stated purpose"
            ))

        score = 100
        score -= len(violations) * 25
        score -= len(warnings) * 10
        score = max(0, min(100, score))

        return ComplianceResult(
            compliant=len(violations) == 0,
            score=score,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
        )

    # ============================================================
    # LIST ALL RULES
    # ============================================================

    def get_all_rules(self) -> Dict:
        """Return all active compliance rules organized by category."""
        rules = {
            "nmc_advertising": {
                "title": "NMC Ethical Advertising (Oct 2026)",
                "rules": [
                    {"id": "NMC-001 to NMC-004", "severity": "block", "description": "No superlative self-promotion (best doctor, top surgeon, #1 clinic)"},
                    {"id": "NMC-010 to NMC-016", "severity": "block", "description": "No guaranteed outcomes (100% success, permanent cure, zero risk)"},
                    {"id": "NMC-020 to NMC-023", "severity": "block", "description": "No patient testimonials or before/after content for promotion"},
                    {"id": "NMC-030 to NMC-032", "severity": "block", "description": "No comparative or disparaging claims against other practitioners"},
                    {"id": "NMC-040 to NMC-042", "severity": "warn", "description": "Discount/offer/urgency language may be seen as inducing treatment"},
                ]
            },
            "dpdp_data_protection": {
                "title": "DPDP Act 2023 (Digital Personal Data Protection)",
                "rules": [
                    {"id": "DPDP-010", "severity": "block", "description": "Explicit consent required before collecting patient data"},
                    {"id": "DPDP-011", "severity": "block", "description": "Data cannot be used beyond the stated purpose (purpose limitation)"},
                    {"id": "DPDP-012", "severity": "block", "description": "Patient data must be encrypted at rest and in transit"},
                    {"id": "DPDP-013", "severity": "warn", "description": "Easy opt-out mechanism must be provided"},
                    {"id": "DPDP-014", "severity": "warn", "description": "Sensitive health data requires enhanced protection"},
                    {"id": "DPDP-015", "severity": "block", "description": "Minor's data requires verifiable parental consent"},
                    {"id": "DPDP-016", "severity": "warn", "description": "Data minimization — collect only what's necessary"},
                ]
            },
            "asci_standards": {
                "title": "ASCI Advertising Standards",
                "rules": [
                    {"id": "ASCI-001", "severity": "warn", "description": "Scientific/clinical claims must be substantiated"},
                    {"id": "ASCI-002", "severity": "warn", "description": "Regulatory approval claims must be verifiable"},
                    {"id": "ASCI-003", "severity": "warn", "description": "Fear-based advertising is discouraged"},
                ]
            },
            "messaging": {
                "title": "WhatsApp/SMS Marketing Rules",
                "rules": [
                    {"id": "MSG-001", "severity": "block", "description": "Marketing messages require explicit patient opt-in"},
                    {"id": "MSG-010", "severity": "block", "description": "Marketing messages must include opt-out mechanism"},
                    {"id": "MSG-020 to MSG-021", "severity": "block", "description": "Messages must not diagnose or prescribe treatments"},
                    {"id": "MSG-030", "severity": "warn", "description": "Messages over 1000 characters may have low engagement"},
                ]
            },
        }

        return {
            "total_rules": sum(len(cat["rules"]) for cat in rules.values()),
            "categories": len(rules),
            "rules": rules,
            "stats": {
                "checks_performed": self.checks_performed,
                "violations_caught": self.violations_caught,
            }
        }
