"""NMC (National Medical Commission) Ad Compliance Filter.

Indian doctors are restricted from certain advertising practices under NMC guidelines:
1. Cannot claim to be "best", "top", "#1" etc. (superlative claims)
2. Cannot promise specific outcomes or cures
3. Cannot use patient testimonials with before/after photos in ads
4. Cannot disparage other doctors or clinics
5. Cannot advertise discounts on medical procedures (some states)
6. Can advertise: clinic name, location, specialties, services, qualifications, timings

This filter checks AI-generated ad copy and blocks/rewrites violations.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Superlative and claim patterns that violate NMC guidelines
BLOCKED_PATTERNS = [
    # Superlatives
    r'\b(best|top|#1|number\s*one|leading|premier|finest|greatest|most\s+experienced)\b',
    r'\b(only|first|sole|exclusive)\s+(clinic|doctor|dentist|surgeon|specialist)\b',
    # Outcome promises
    r'\b(guaranteed|100%|sure\s+cure|permanent\s+cure|instant\s+relief)\b',
    r'\b(pain\s*free|painless)\s+(treatment|procedure|surgery)\b',  # specific medical claim
    r'\b(no\s+side\s+effects?|zero\s+risk|risk\s*free)\b',
    # Comparative disparagement
    r'\b(better\s+than|unlike\s+other|other\s+clinics?\s+(fail|can\'?t|don\'?t))\b',
    r'\b(cheapest|lowest\s+price|lowest\s+cost)\b',
    # Discount advertising (grey area in some states)
    r'\b(\d+%\s+off|flat\s+discount|free\s+treatment|free\s+consultation)\b',
]

# Compile patterns for performance
_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]

# Safe replacement suggestions
SAFE_ALTERNATIVES = {
    "best": "experienced",
    "top": "qualified",
    "#1": "trusted",
    "number one": "trusted",
    "leading": "established",
    "guaranteed": "effective",
    "100%": "high success rate",
    "painless": "comfortable",
    "cheapest": "affordable",
    "lowest price": "competitive pricing",
    "free consultation": "consultation available",
}


def check_ad_compliance(text: str) -> dict:
    """Check ad copy for NMC compliance violations.

    Returns:
        {
            "compliant": bool,
            "violations": [{"pattern": str, "match": str, "suggestion": str}],
            "cleaned_text": str (with violations replaced),
        }
    """
    violations = []
    cleaned = text

    for i, pattern in enumerate(_COMPILED_PATTERNS):
        matches = pattern.findall(text)
        for match in matches:
            match_str = match if isinstance(match, str) else match[0]
            suggestion = SAFE_ALTERNATIVES.get(match_str.lower(), "remove this claim")
            violations.append({
                "pattern": BLOCKED_PATTERNS[i],
                "match": match_str,
                "suggestion": f"Replace '{match_str}' with '{suggestion}'" if suggestion != "remove this claim" else f"Remove '{match_str}'",
            })
            # Auto-replace known violations
            if match_str.lower() in SAFE_ALTERNATIVES:
                cleaned = re.sub(
                    re.escape(match_str),
                    SAFE_ALTERNATIVES[match_str.lower()],
                    cleaned,
                    flags=re.IGNORECASE,
                    count=1,
                )

    compliant = len(violations) == 0

    if not compliant:
        logger.warning("NMC compliance violations found in ad copy: %s", [v["match"] for v in violations])

    return {
        "compliant": compliant,
        "violations": violations,
        "cleaned_text": cleaned,
        "original_text": text,
    }


def validate_ad_headlines(headlines: list[str]) -> dict:
    """Validate a list of ad headlines for compliance."""
    results = []
    all_compliant = True
    for h in headlines:
        result = check_ad_compliance(h)
        results.append(result)
        if not result["compliant"]:
            all_compliant = False

    return {
        "all_compliant": all_compliant,
        "headlines": results,
        "cleaned_headlines": [r["cleaned_text"] for r in results],
    }


def validate_ad_descriptions(descriptions: list[str]) -> dict:
    """Validate ad descriptions for compliance."""
    results = []
    all_compliant = True
    for d in descriptions:
        result = check_ad_compliance(d)
        results.append(result)
        if not result["compliant"]:
            all_compliant = False

    return {
        "all_compliant": all_compliant,
        "descriptions": results,
        "cleaned_descriptions": [r["cleaned_text"] for r in results],
    }
