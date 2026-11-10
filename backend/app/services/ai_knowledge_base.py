"""
PatientPlex AI Knowledge Base — All verified benchmark data, specialty knowledge,
and campaign intelligence fed into the AI models.

This is the "brain" that every other service queries:
- AI Receptionist uses it to know treatment costs and booking patterns
- Google Ads engine uses it to set initial bids and budgets
- Campaign templates use it to create specialty-specific campaigns
- ML models use it as seed data before real clinic data accumulates
- Compliance checker uses it for NMC rule awareness

Sources (verified Q2 2026):
- ICG (iChelon Consulting Group) — 65+ live accounts, ₹40Cr annual healthcare spend
- OwlClaw India PPC Benchmarks 2026
- upGrowth Google Ads India 2026
- Practo India Specialty Care GMV data
- ClickMaking healthcare case studies
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Specialty(str, Enum):
    DENTAL_GENERAL = "dental_general"
    DENTAL_IMPLANTS = "dental_implants"
    DERMATOLOGY_MEDICAL = "dermatology_medical"
    DERMATOLOGY_COSMETIC = "dermatology_cosmetic"
    HAIR_TRANSPLANT = "hair_transplant"
    IVF_FERTILITY = "ivf_fertility"
    ORTHOPEDIC = "orthopedic"
    OPHTHALMOLOGY = "ophthalmology"
    GYNECOLOGY = "gynecology"
    ENT = "ent"
    PEDIATRIC = "pediatric"
    COSMETIC_SURGERY = "cosmetic_surgery"
    CARDIOLOGY = "cardiology"
    UROLOGY = "urology"
    GASTROENTEROLOGY = "gastroenterology"
    NEUROLOGY_PSYCHIATRY = "neurology_psychiatry"
    PHYSIOTHERAPY = "physiotherapy"
    AYURVEDA = "ayurveda"


class CityTier(str, Enum):
    TIER_1 = "tier_1"  # Mumbai, Delhi NCR, Bangalore, Chennai, Hyderabad, Kolkata
    TIER_2 = "tier_2"  # Pune, Ahmedabad, Jaipur, Chandigarh, Lucknow, Indore, Kochi
    TIER_3 = "tier_3"  # Smaller cities


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class SpecialtyBenchmark:
    """Verified benchmark data for a healthcare specialty."""
    specialty: Specialty
    # Google Ads benchmarks (₹)
    google_cpc_low: float
    google_cpc_high: float
    google_cpl_low: float
    google_cpl_high: float
    google_cpql_top_quartile: float  # ICG top-quartile CPQL
    google_cpql_market_median: float  # Market median CPQL
    google_conversion_rate_low: float  # Click→Lead %
    google_conversion_rate_high: float
    google_appointment_cost_multiplier: float  # Appointment cost = CPL × this (4-8x)
    # Meta Ads benchmarks (₹)
    meta_ctwa_cpl_low: float  # Click-to-WhatsApp CPL
    meta_ctwa_cpl_high: float
    meta_form_cpl_low: float
    meta_form_cpl_high: float
    meta_cpql_low: float
    meta_cpql_high: float
    meta_qualified_rate_low: float  # % of leads that are qualified
    meta_qualified_rate_high: float
    # Treatment economics (₹)
    consultation_fee_low: float
    consultation_fee_high: float
    avg_treatment_value: float  # Blended ATV
    high_value_treatment: str  # Name of highest-value treatment
    high_value_treatment_cost: float
    patient_consideration_days: int  # How long patient thinks before booking
    repeat_visit_rate: float  # % of patients who return within 12 months
    lifetime_value_months: int  # Average patient relationship duration
    # Campaign settings
    recommended_daily_budget_low: float
    recommended_daily_budget_high: float
    recommended_geo_radius_km: int
    peak_search_hours: List[int]  # Hours of day with highest search volume
    peak_search_days: List[int]  # Days of week (0=Mon, 6=Sun)
    # Content
    top_keywords: List[str]
    negative_keywords: List[str]
    reel_topics: List[str]
    patient_questions: List[str]  # FAQs the AI receptionist should answer
    # NMC compliance
    banned_claims: List[str]  # Claims that violate NMC advertising rules


# ---------------------------------------------------------------------------
# THE KNOWLEDGE BASE — Every specialty's verified data
# ---------------------------------------------------------------------------

SPECIALTY_BENCHMARKS: Dict[Specialty, SpecialtyBenchmark] = {

    Specialty.DENTAL_GENERAL: SpecialtyBenchmark(
        specialty=Specialty.DENTAL_GENERAL,
        # Google Ads — Source: ICG 2026
        google_cpc_low=35, google_cpc_high=95,
        google_cpl_low=120, google_cpl_high=380,
        google_cpql_top_quartile=320, google_cpql_market_median=620,
        google_conversion_rate_low=6, google_conversion_rate_high=14,
        google_appointment_cost_multiplier=4,
        # Meta Ads — Source: ICG Meta Benchmark 2026
        meta_ctwa_cpl_low=180, meta_ctwa_cpl_high=380,
        meta_form_cpl_low=420, meta_form_cpl_high=880,
        meta_cpql_low=520, meta_cpql_high=900,
        meta_qualified_rate_low=32, meta_qualified_rate_high=45,
        # Treatment economics — Source: Practo GMV
        consultation_fee_low=200, consultation_fee_high=500,
        avg_treatment_value=3800,
        high_value_treatment="Root Canal", high_value_treatment_cost=8000,
        patient_consideration_days=3,
        repeat_visit_rate=40, lifetime_value_months=24,
        # Campaign settings
        recommended_daily_budget_low=400, recommended_daily_budget_high=800,
        recommended_geo_radius_km=5,
        peak_search_hours=[9, 10, 11, 14, 15, 16, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4],  # Weekdays
        # Content
        top_keywords=[
            "dentist near me", "dental clinic near me", "tooth pain doctor",
            "root canal treatment {city}", "teeth cleaning cost",
            "dental implant {city}", "braces cost {city}",
            "wisdom tooth removal", "teeth whitening {city}",
            "best dentist in {city}", "emergency dentist {city}",
        ],
        negative_keywords=[
            "dental college", "dental admission", "BDS course", "dental salary",
            "dental assistant jobs", "dental hygienist", "free dental",
            "dental insurance", "how to become dentist", "dental exam paper",
            "home remedy", "diy teeth whitening",
        ],
        reel_topics=[
            "Root canal myth busting — it's painless!",
            "When to get implants vs bridge — the truth",
            "Why your teeth are yellowing (it's not what you think)",
            "Braces vs aligners — which is right for you?",
            "5 signs you need a dentist TODAY",
            "How much does a root canal cost in {city}?",
        ],
        patient_questions=[
            "How much does {treatment} cost?",
            "Is the procedure painful?",
            "How long does the treatment take?",
            "Do you accept insurance?",
            "What are your clinic timings?",
            "Where is the clinic located?",
            "Can I book for this weekend?",
            "Do you do emergency appointments?",
        ],
        banned_claims=[
            "best dentist", "number one", "guaranteed results",
            "painless guaranteed", "100% success", "cheapest",
            "testimonial from patient", "before after photos in ads",
        ],
    ),

    Specialty.DENTAL_IMPLANTS: SpecialtyBenchmark(
        specialty=Specialty.DENTAL_IMPLANTS,
        google_cpc_low=90, google_cpc_high=250,
        google_cpl_low=450, google_cpl_high=1600,
        google_cpql_top_quartile=950, google_cpql_market_median=1750,
        google_conversion_rate_low=4, google_conversion_rate_high=8,
        google_appointment_cost_multiplier=5,
        meta_ctwa_cpl_low=280, meta_ctwa_cpl_high=580,
        meta_form_cpl_low=680, meta_form_cpl_high=1400,
        meta_cpql_low=820, meta_cpql_high=1400,
        meta_qualified_rate_low=28, meta_qualified_rate_high=40,
        consultation_fee_low=500, consultation_fee_high=1000,
        avg_treatment_value=35000,
        high_value_treatment="Full Mouth Implants", high_value_treatment_cost=300000,
        patient_consideration_days=14,
        repeat_visit_rate=20, lifetime_value_months=36,
        recommended_daily_budget_low=800, recommended_daily_budget_high=2000,
        recommended_geo_radius_km=15,
        peak_search_hours=[10, 11, 14, 15, 20, 21, 22],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=[
            "dental implant cost {city}", "dental implant near me",
            "teeth implant price", "single tooth implant cost",
            "full mouth implant cost india", "all on 4 implants {city}",
            "dental implant clinic {city}", "implant vs bridge",
            "best implant dentist {city}", "implant surgery cost",
        ],
        negative_keywords=[
            "dental implant course", "implant training", "implant manufacturer",
            "dental implant company", "implant supplier", "free implant",
            "implant failure", "implant removal",
        ],
        reel_topics=[
            "Dental implant in 60 seconds — what actually happens",
            "Implant vs bridge vs denture — honest comparison",
            "How long do dental implants last?",
            "Full mouth implants — ₹3L vs ₹30L, what's the difference?",
        ],
        patient_questions=[
            "How much does a single implant cost?",
            "How long does the implant procedure take?",
            "Is it painful? What about anesthesia?",
            "How long before I can eat normally?",
            "What is the success rate?",
            "Do you offer EMI/payment plans?",
            "How long do implants last?",
        ],
        banned_claims=[
            "best implant surgeon", "guaranteed success", "painless implant",
            "cheapest implant", "100% success rate",
        ],
    ),

    Specialty.DERMATOLOGY_COSMETIC: SpecialtyBenchmark(
        specialty=Specialty.DERMATOLOGY_COSMETIC,
        google_cpc_low=55, google_cpc_high=200,
        google_cpl_low=280, google_cpl_high=700,
        google_cpql_top_quartile=820, google_cpql_market_median=1650,
        google_conversion_rate_low=5, google_conversion_rate_high=10,
        google_appointment_cost_multiplier=5,
        meta_ctwa_cpl_low=240, meta_ctwa_cpl_high=480,
        meta_form_cpl_low=580, meta_form_cpl_high=1200,
        meta_cpql_low=680, meta_cpql_high=1200,
        meta_qualified_rate_low=28, meta_qualified_rate_high=42,
        consultation_fee_low=500, consultation_fee_high=1500,
        avg_treatment_value=18000,
        high_value_treatment="Full Body Laser Hair Removal", high_value_treatment_cost=120000,
        patient_consideration_days=7,
        repeat_visit_rate=65, lifetime_value_months=18,
        recommended_daily_budget_low=500, recommended_daily_budget_high=1500,
        recommended_geo_radius_km=10,
        peak_search_hours=[10, 11, 13, 14, 20, 21, 22],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=[
            "laser hair removal {city}", "botox {city}",
            "PRP treatment cost {city}", "acne scar treatment",
            "skin tightening cost", "hydrafacial near me",
            "chemical peel {city}", "dermatologist near me",
            "skin whitening treatment", "anti aging treatment {city}",
        ],
        negative_keywords=[
            "dermatology course", "dermatologist salary", "home remedy acne",
            "DIY skin care", "natural remedies", "dermatology college",
        ],
        reel_topics=[
            "Laser hair removal — everything you need to know in 60 seconds",
            "PRP for hair growth — does it actually work?",
            "Botox vs fillers — which one do you need?",
            "Chemical peel recovery — day by day",
            "This is what's REALLY causing your acne",
            "HydraFacial — is it worth ₹3,000?",
        ],
        patient_questions=[
            "How many sessions will I need?",
            "How much does {treatment} cost per session?",
            "Is there any downtime?",
            "What results can I expect?",
            "Is it safe for my skin type?",
            "Do you offer packages?",
        ],
        banned_claims=[
            "guaranteed results", "permanent solution", "100% safe",
            "before after photos", "celebrity skin", "best dermatologist",
        ],
    ),

    Specialty.HAIR_TRANSPLANT: SpecialtyBenchmark(
        specialty=Specialty.HAIR_TRANSPLANT,
        google_cpc_low=45, google_cpc_high=120,
        google_cpl_low=380, google_cpl_high=850,
        google_cpql_top_quartile=820, google_cpql_market_median=1600,
        google_conversion_rate_low=6, google_conversion_rate_high=12,
        google_appointment_cost_multiplier=4,
        meta_ctwa_cpl_low=380, meta_ctwa_cpl_high=680,
        meta_form_cpl_low=880, meta_form_cpl_high=1400,
        meta_cpql_low=1400, meta_cpql_high=2200,
        meta_qualified_rate_low=25, meta_qualified_rate_high=35,
        consultation_fee_low=500, consultation_fee_high=1000,
        avg_treatment_value=85000,
        high_value_treatment="FUE 3000+ Grafts", high_value_treatment_cost=200000,
        patient_consideration_days=21,
        repeat_visit_rate=15, lifetime_value_months=12,
        recommended_daily_budget_low=1000, recommended_daily_budget_high=2500,
        recommended_geo_radius_km=25,
        peak_search_hours=[10, 11, 14, 15, 21, 22, 23],
        peak_search_days=[0, 1, 2, 3, 4, 5, 6],
        top_keywords=[
            "hair transplant cost {city}", "hair transplant near me",
            "FUE hair transplant cost", "hair transplant cost per graft",
            "best hair transplant clinic {city}", "hair transplant before after",
            "hair transplant results", "hair loss treatment {city}",
            "PRP for hair loss cost", "beard transplant cost",
        ],
        negative_keywords=[
            "hair transplant training", "hair transplant course",
            "hair transplant gone wrong", "failed hair transplant",
            "hair transplant technician job",
        ],
        reel_topics=[
            "FUE vs FUT — which one should you choose?",
            "Hair transplant — day by day recovery timeline",
            "How much does hair transplant cost in {city}?",
            "Who is NOT a good candidate for hair transplant",
            "1000 grafts vs 3000 grafts — what's the difference?",
        ],
        patient_questions=[
            "How much does it cost per graft?",
            "How many grafts do I need?",
            "How long is the recovery?",
            "When will I see results?",
            "Will it look natural?",
            "Do you offer EMI?",
            "What's the success rate?",
        ],
        banned_claims=[
            "guaranteed regrowth", "100% natural", "best surgeon",
            "no side effects", "painless procedure", "permanent solution guaranteed",
        ],
    ),

    Specialty.IVF_FERTILITY: SpecialtyBenchmark(
        specialty=Specialty.IVF_FERTILITY,
        google_cpc_low=85, google_cpc_high=220,
        google_cpl_low=450, google_cpl_high=1600,
        google_cpql_top_quartile=1120, google_cpql_market_median=2200,
        google_conversion_rate_low=4.5, google_conversion_rate_high=9,
        google_appointment_cost_multiplier=6,
        meta_ctwa_cpl_low=420, meta_ctwa_cpl_high=680,
        meta_form_cpl_low=980, meta_form_cpl_high=1800,
        meta_cpql_low=980, meta_cpql_high=1400,
        meta_qualified_rate_low=38, meta_qualified_rate_high=52,
        consultation_fee_low=500, consultation_fee_high=2000,
        avg_treatment_value=150000,
        high_value_treatment="IVF Cycle with ICSI", high_value_treatment_cost=250000,
        patient_consideration_days=45,
        repeat_visit_rate=60, lifetime_value_months=18,
        recommended_daily_budget_low=1500, recommended_daily_budget_high=5000,
        recommended_geo_radius_km=30,
        peak_search_hours=[9, 10, 11, 14, 15, 20, 21, 22],
        peak_search_days=[0, 1, 2, 3, 4, 5, 6],
        top_keywords=[
            "IVF cost {city}", "IVF center near me", "fertility clinic {city}",
            "IVF success rate", "IUI treatment cost", "ICSI treatment cost",
            "egg freezing cost {city}", "male infertility treatment",
            "best IVF doctor {city}", "IVF with donor egg cost",
        ],
        negative_keywords=[
            "IVF course", "IVF training", "embryologist job",
            "IVF failure stories", "IVF risks death",
        ],
        reel_topics=[
            "IVF — everything you need to know in 60 seconds",
            "IVF success rate by age — the honest numbers",
            "IUI vs IVF — which is right for you?",
            "5 things to know before starting IVF",
            "Male infertility — myths busted",
        ],
        patient_questions=[
            "What is the success rate?",
            "How much does one IVF cycle cost?",
            "How many cycles will I need?",
            "Is it painful?",
            "What tests do I need before starting?",
            "Do you have EMI options?",
            "Can I work during the IVF cycle?",
            "What is the age limit for IVF?",
        ],
        banned_claims=[
            "guaranteed pregnancy", "100% success", "best IVF center",
            "highest success rate", "painless IVF",
        ],
    ),

    Specialty.ORTHOPEDIC: SpecialtyBenchmark(
        specialty=Specialty.ORTHOPEDIC,
        google_cpc_low=95, google_cpc_high=350,
        google_cpl_low=450, google_cpl_high=1200,
        google_cpql_top_quartile=1400, google_cpql_market_median=2800,
        google_conversion_rate_low=3, google_conversion_rate_high=7,
        google_appointment_cost_multiplier=6,
        meta_ctwa_cpl_low=320, meta_ctwa_cpl_high=600,
        meta_form_cpl_low=680, meta_form_cpl_high=1400,
        meta_cpql_low=900, meta_cpql_high=1600,
        meta_qualified_rate_low=25, meta_qualified_rate_high=38,
        consultation_fee_low=500, consultation_fee_high=1500,
        avg_treatment_value=22000,
        high_value_treatment="Total Knee Replacement", high_value_treatment_cost=300000,
        patient_consideration_days=14,
        repeat_visit_rate=30, lifetime_value_months=12,
        recommended_daily_budget_low=600, recommended_daily_budget_high=1800,
        recommended_geo_radius_km=15,
        peak_search_hours=[8, 9, 10, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4],
        top_keywords=[
            "orthopedic doctor near me", "knee pain treatment {city}",
            "joint replacement cost {city}", "sports injury doctor",
            "back pain specialist {city}", "knee replacement cost",
            "spine specialist {city}", "fracture treatment near me",
        ],
        negative_keywords=[
            "orthopedic course", "MBBS orthopedic", "orthopedic surgeon salary",
            "orthopedic shoes", "orthopedic mattress",
        ],
        reel_topics=[
            "Knee pain at 30? Here's what's happening",
            "Do you REALLY need knee surgery? (honest answer)",
            "Physiotherapy vs surgery for back pain",
            "Knee replacement — what to expect day by day",
        ],
        patient_questions=[
            "Do I need surgery or can it be treated without?",
            "How much does joint replacement cost?",
            "How long is the recovery?",
            "Will I be able to walk normally after surgery?",
            "Do you accept insurance/cashless?",
        ],
        banned_claims=[
            "best orthopedic surgeon", "guaranteed recovery",
            "painless surgery", "walk the next day guaranteed",
        ],
    ),

    Specialty.OPHTHALMOLOGY: SpecialtyBenchmark(
        specialty=Specialty.OPHTHALMOLOGY,
        google_cpc_low=65, google_cpc_high=180,
        google_cpl_low=220, google_cpl_high=520,
        google_cpql_top_quartile=640, google_cpql_market_median=1250,
        google_conversion_rate_low=5, google_conversion_rate_high=9,
        google_appointment_cost_multiplier=5,
        meta_ctwa_cpl_low=220, meta_ctwa_cpl_high=440,
        meta_form_cpl_low=520, meta_form_cpl_high=980,
        meta_cpql_low=620, meta_cpql_high=1100,
        meta_qualified_rate_low=30, meta_qualified_rate_high=42,
        consultation_fee_low=300, consultation_fee_high=1000,
        avg_treatment_value=28000,
        high_value_treatment="LASIK Surgery", high_value_treatment_cost=50000,
        patient_consideration_days=10,
        repeat_visit_rate=25, lifetime_value_months=12,
        recommended_daily_budget_low=600, recommended_daily_budget_high=1500,
        recommended_geo_radius_km=15,
        peak_search_hours=[9, 10, 11, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=[
            "LASIK surgery cost {city}", "eye specialist near me",
            "cataract surgery cost", "specs removal surgery {city}",
            "eye hospital near me", "glaucoma treatment {city}",
            "LASIK vs PRK", "retina specialist {city}",
        ],
        negative_keywords=[
            "ophthalmology course", "eye doctor salary", "optometry college",
            "eye drops", "contact lens", "spectacle shop",
        ],
        reel_topics=[
            "LASIK — everything you need to know in 60 seconds",
            "Cataract surgery — what actually happens inside",
            "Specs removal — LASIK vs ICL vs SMILE",
            "5 warning signs your eyes need a doctor NOW",
        ],
        patient_questions=[
            "Am I eligible for LASIK?",
            "How much does LASIK cost?",
            "Is the procedure painful?",
            "How long does it take to recover?",
            "What's the success rate?",
            "Can I go back to work the next day?",
        ],
        banned_claims=[
            "best eye hospital", "guaranteed 6/6 vision", "painless guaranteed",
            "100% safe", "cheapest LASIK",
        ],
    ),

    Specialty.GYNECOLOGY: SpecialtyBenchmark(
        specialty=Specialty.GYNECOLOGY,
        google_cpc_low=40, google_cpc_high=110,
        google_cpl_low=250, google_cpl_high=700,
        google_cpql_top_quartile=500, google_cpql_market_median=1000,
        google_conversion_rate_low=5, google_conversion_rate_high=10,
        google_appointment_cost_multiplier=4,
        meta_ctwa_cpl_low=200, meta_ctwa_cpl_high=400,
        meta_form_cpl_low=450, meta_form_cpl_high=900,
        meta_cpql_low=600, meta_cpql_high=1000,
        meta_qualified_rate_low=30, meta_qualified_rate_high=45,
        consultation_fee_low=300, consultation_fee_high=800,
        avg_treatment_value=6500,
        high_value_treatment="C-Section Delivery", high_value_treatment_cost=150000,
        patient_consideration_days=5,
        repeat_visit_rate=50, lifetime_value_months=24,
        recommended_daily_budget_low=400, recommended_daily_budget_high=1000,
        recommended_geo_radius_km=10,
        peak_search_hours=[9, 10, 11, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=[
            "gynecologist near me", "PCOD treatment {city}",
            "pregnancy doctor near me", "best gynecologist {city}",
            "irregular periods treatment", "fibroid treatment cost",
            "normal delivery hospital {city}", "PCOS specialist {city}",
        ],
        negative_keywords=[
            "gynecology course", "MBBS gynecology", "gynecologist salary",
            "home remedy PCOD", "pregnancy tips",
        ],
        reel_topics=[
            "PCOD vs PCOS — what's the difference?",
            "5 signs you should see a gynecologist",
            "Irregular periods — when to worry",
            "Normal delivery vs C-section — honest talk",
        ],
        patient_questions=[
            "What are your consultation fees?",
            "Do you handle high-risk pregnancies?",
            "What tests do I need for PCOD?",
            "Do you have female doctors?",
            "Do you accept insurance for delivery?",
        ],
        banned_claims=[
            "best gynecologist", "guaranteed normal delivery",
            "painless delivery guaranteed", "100% safe",
        ],
    ),

    # Remaining specialties with concise data...

    Specialty.DERMATOLOGY_MEDICAL: SpecialtyBenchmark(
        specialty=Specialty.DERMATOLOGY_MEDICAL,
        google_cpc_low=45, google_cpc_high=140,
        google_cpl_low=280, google_cpl_high=700,
        google_cpql_top_quartile=540, google_cpql_market_median=1100,
        google_conversion_rate_low=5, google_conversion_rate_high=10,
        google_appointment_cost_multiplier=4,
        meta_ctwa_cpl_low=200, meta_ctwa_cpl_high=380,
        meta_form_cpl_low=450, meta_form_cpl_high=900,
        meta_cpql_low=550, meta_cpql_high=1000,
        meta_qualified_rate_low=30, meta_qualified_rate_high=42,
        consultation_fee_low=300, consultation_fee_high=800,
        avg_treatment_value=4500,
        high_value_treatment="Psoriasis Biologic Therapy", high_value_treatment_cost=50000,
        patient_consideration_days=5,
        repeat_visit_rate=55, lifetime_value_months=18,
        recommended_daily_budget_low=400, recommended_daily_budget_high=1000,
        recommended_geo_radius_km=8,
        peak_search_hours=[9, 10, 11, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=["dermatologist near me", "skin doctor near me", "acne treatment {city}", "eczema treatment", "psoriasis specialist {city}", "fungal infection treatment", "skin allergy doctor"],
        negative_keywords=["dermatology course", "dermatologist salary", "home remedy", "DIY skin care"],
        reel_topics=["This is what's actually causing your acne", "Eczema vs psoriasis — how to tell", "When to see a dermatologist (not just use cream)"],
        patient_questions=["How much does consultation cost?", "Do you treat {condition}?", "How many visits will I need?", "Is it contagious?"],
        banned_claims=["best dermatologist", "guaranteed cure", "100% safe"],
    ),

    Specialty.ENT: SpecialtyBenchmark(
        specialty=Specialty.ENT,
        google_cpc_low=35, google_cpc_high=90,
        google_cpl_low=200, google_cpl_high=600,
        google_cpql_top_quartile=400, google_cpql_market_median=800,
        google_conversion_rate_low=6, google_conversion_rate_high=12,
        google_appointment_cost_multiplier=4,
        meta_ctwa_cpl_low=180, meta_ctwa_cpl_high=350,
        meta_form_cpl_low=400, meta_form_cpl_high=800,
        meta_cpql_low=500, meta_cpql_high=900,
        meta_qualified_rate_low=32, meta_qualified_rate_high=45,
        consultation_fee_low=300, consultation_fee_high=700,
        avg_treatment_value=5200,
        high_value_treatment="FESS (Sinus Surgery)", high_value_treatment_cost=60000,
        patient_consideration_days=5,
        repeat_visit_rate=30, lifetime_value_months=12,
        recommended_daily_budget_low=300, recommended_daily_budget_high=700,
        recommended_geo_radius_km=8,
        peak_search_hours=[8, 9, 10, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=["ENT doctor near me", "ear specialist near me", "sinus treatment {city}", "tonsil surgery cost", "hearing loss doctor", "snoring treatment", "vertigo specialist"],
        negative_keywords=["ENT course", "ENT salary", "home remedy ear pain"],
        reel_topics=["Sinusitis — when you need surgery vs medicine", "Snoring is not normal — here's why", "Tonsil surgery — what to expect"],
        patient_questions=["Do I need surgery?", "How much does sinus surgery cost?", "Is it painful?", "How long is recovery?"],
        banned_claims=["best ENT", "guaranteed cure", "painless guaranteed"],
    ),

    Specialty.PEDIATRIC: SpecialtyBenchmark(
        specialty=Specialty.PEDIATRIC,
        google_cpc_low=25, google_cpc_high=80,
        google_cpl_low=120, google_cpl_high=300,
        google_cpql_top_quartile=250, google_cpql_market_median=500,
        google_conversion_rate_low=8, google_conversion_rate_high=15,
        google_appointment_cost_multiplier=3,
        meta_ctwa_cpl_low=150, meta_ctwa_cpl_high=300,
        meta_form_cpl_low=350, meta_form_cpl_high=700,
        meta_cpql_low=400, meta_cpql_high=700,
        meta_qualified_rate_low=38, meta_qualified_rate_high=52,
        consultation_fee_low=300, consultation_fee_high=600,
        avg_treatment_value=1800,
        high_value_treatment="Allergy Testing", high_value_treatment_cost=5000,
        patient_consideration_days=1,
        repeat_visit_rate=70, lifetime_value_months=36,
        recommended_daily_budget_low=250, recommended_daily_budget_high=500,
        recommended_geo_radius_km=5,
        peak_search_hours=[7, 8, 9, 10, 19, 20, 21, 22],
        peak_search_days=[0, 1, 2, 3, 4, 5, 6],
        top_keywords=["pediatrician near me", "child doctor near me", "vaccination schedule", "baby doctor {city}", "child specialist {city}", "newborn doctor"],
        negative_keywords=["pediatric course", "pediatrician salary", "child home remedy"],
        reel_topics=["Vaccination schedule 2026 — complete guide", "When to take your child to the ER", "Common childhood allergies — what parents should know"],
        patient_questions=["What vaccinations does my child need?", "Is this fever serious?", "Do you see newborns?", "What are your charges?"],
        banned_claims=["best pediatrician", "guaranteed health", "100% safe vaccines"],
    ),

    Specialty.COSMETIC_SURGERY: SpecialtyBenchmark(
        specialty=Specialty.COSMETIC_SURGERY,
        google_cpc_low=140, google_cpc_high=340,
        google_cpl_low=480, google_cpl_high=1100,
        google_cpql_top_quartile=1800, google_cpql_market_median=3200,
        google_conversion_rate_low=3, google_conversion_rate_high=6,
        google_appointment_cost_multiplier=7,
        meta_ctwa_cpl_low=680, meta_ctwa_cpl_high=1200,
        meta_form_cpl_low=1800, meta_form_cpl_high=3400,
        meta_cpql_low=2400, meta_cpql_high=4200,
        meta_qualified_rate_low=22, meta_qualified_rate_high=32,
        consultation_fee_low=1000, consultation_fee_high=3000,
        avg_treatment_value=150000,
        high_value_treatment="Rhinoplasty", high_value_treatment_cost=200000,
        patient_consideration_days=30,
        repeat_visit_rate=25, lifetime_value_months=24,
        recommended_daily_budget_low=1500, recommended_daily_budget_high=5000,
        recommended_geo_radius_km=30,
        peak_search_hours=[10, 11, 14, 15, 21, 22, 23],
        peak_search_days=[0, 1, 2, 3, 4, 5, 6],
        top_keywords=["rhinoplasty cost {city}", "liposuction cost india", "tummy tuck cost", "facelift cost {city}", "plastic surgeon near me", "cosmetic surgery {city}"],
        negative_keywords=["plastic surgery gone wrong", "plastic surgery training", "cosmetic surgery risks death"],
        reel_topics=["Rhinoplasty — what actually happens (60 seconds)", "Liposuction vs diet — honest answer", "Recovery timeline after cosmetic surgery"],
        patient_questions=["How much does the procedure cost?", "What are the risks?", "How long is recovery?", "Will it look natural?", "Do you offer EMI?"],
        banned_claims=["best plastic surgeon", "guaranteed results", "risk-free", "painless", "celebrity surgeon"],
    ),

    Specialty.CARDIOLOGY: SpecialtyBenchmark(
        specialty=Specialty.CARDIOLOGY,
        google_cpc_low=120, google_cpc_high=450,
        google_cpl_low=500, google_cpl_high=1300,
        google_cpql_top_quartile=3200, google_cpql_market_median=5400,
        google_conversion_rate_low=3, google_conversion_rate_high=5,
        google_appointment_cost_multiplier=8,
        meta_ctwa_cpl_low=350, meta_ctwa_cpl_high=700,
        meta_form_cpl_low=800, meta_form_cpl_high=1600,
        meta_cpql_low=1200, meta_cpql_high=2200,
        meta_qualified_rate_low=22, meta_qualified_rate_high=35,
        consultation_fee_low=500, consultation_fee_high=2000,
        avg_treatment_value=18300,
        high_value_treatment="Angioplasty (PCI)", high_value_treatment_cost=300000,
        patient_consideration_days=3,
        repeat_visit_rate=60, lifetime_value_months=36,
        recommended_daily_budget_low=700, recommended_daily_budget_high=2500,
        recommended_geo_radius_km=20,
        peak_search_hours=[8, 9, 10, 14, 15, 16, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=["cardiologist near me", "heart specialist {city}", "angioplasty cost {city}", "heart checkup {city}", "chest pain doctor", "ECG test near me"],
        negative_keywords=["cardiology course", "cardiologist salary", "heart attack first aid"],
        reel_topics=["5 heart attack warning signs you're ignoring", "Angioplasty vs bypass — which do you need?", "Heart checkup at 30 — what tests you need"],
        patient_questions=["Do I need angioplasty?", "How much does it cost?", "Is bypass surgery necessary?", "Do you accept insurance?"],
        banned_claims=["best cardiologist", "guaranteed survival", "100% safe surgery"],
    ),

    Specialty.UROLOGY: SpecialtyBenchmark(
        specialty=Specialty.UROLOGY,
        google_cpc_low=50, google_cpc_high=130,
        google_cpl_low=300, google_cpl_high=800,
        google_cpql_top_quartile=600, google_cpql_market_median=1200,
        google_conversion_rate_low=5, google_conversion_rate_high=9,
        google_appointment_cost_multiplier=5,
        meta_ctwa_cpl_low=250, meta_ctwa_cpl_high=500,
        meta_form_cpl_low=550, meta_form_cpl_high=1100,
        meta_cpql_low=700, meta_cpql_high=1300,
        meta_qualified_rate_low=28, meta_qualified_rate_high=40,
        consultation_fee_low=400, consultation_fee_high=1000,
        avg_treatment_value=12000,
        high_value_treatment="Kidney Stone RIRS/PCNL", high_value_treatment_cost=80000,
        patient_consideration_days=5,
        repeat_visit_rate=25, lifetime_value_months=12,
        recommended_daily_budget_low=400, recommended_daily_budget_high=1000,
        recommended_geo_radius_km=10,
        peak_search_hours=[9, 10, 11, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=["urologist near me", "kidney stone treatment {city}", "prostate treatment {city}", "UTI doctor", "circumcision cost {city}", "kidney stone removal cost"],
        negative_keywords=["urology course", "urologist salary"],
        reel_topics=["Kidney stones — prevention tips that actually work", "When to see a urologist (most men wait too long)"],
        patient_questions=["How much does kidney stone treatment cost?", "Do I need surgery?", "Is it painful?"],
        banned_claims=["best urologist", "painless guaranteed", "100% stone removal"],
    ),

    Specialty.GASTROENTEROLOGY: SpecialtyBenchmark(
        specialty=Specialty.GASTROENTEROLOGY,
        google_cpc_low=45, google_cpc_high=120,
        google_cpl_low=300, google_cpl_high=700,
        google_cpql_top_quartile=550, google_cpql_market_median=1100,
        google_conversion_rate_low=5, google_conversion_rate_high=10,
        google_appointment_cost_multiplier=4,
        meta_ctwa_cpl_low=220, meta_ctwa_cpl_high=450,
        meta_form_cpl_low=500, meta_form_cpl_high=1000,
        meta_cpql_low=650, meta_cpql_high=1200,
        meta_qualified_rate_low=28, meta_qualified_rate_high=40,
        consultation_fee_low=400, consultation_fee_high=1000,
        avg_treatment_value=8500,
        high_value_treatment="Endoscopy + Colonoscopy", high_value_treatment_cost=25000,
        patient_consideration_days=5,
        repeat_visit_rate=35, lifetime_value_months=12,
        recommended_daily_budget_low=350, recommended_daily_budget_high=800,
        recommended_geo_radius_km=10,
        peak_search_hours=[8, 9, 10, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=["gastroenterologist near me", "stomach doctor", "piles treatment {city}", "endoscopy cost", "colonoscopy {city}", "liver specialist", "acidity treatment"],
        negative_keywords=["gastroenterology course", "home remedy acidity", "piles home treatment"],
        reel_topics=["Piles — when you need surgery vs medicine", "Endoscopy — what to expect", "Acidity vs GERD — know the difference"],
        patient_questions=["How much does endoscopy cost?", "Is the procedure painful?", "Do I need to fast before?"],
        banned_claims=["best gastroenterologist", "guaranteed cure", "painless"],
    ),

    Specialty.NEUROLOGY_PSYCHIATRY: SpecialtyBenchmark(
        specialty=Specialty.NEUROLOGY_PSYCHIATRY,
        google_cpc_low=40, google_cpc_high=120,
        google_cpl_low=300, google_cpl_high=900,
        google_cpql_top_quartile=600, google_cpql_market_median=1200,
        google_conversion_rate_low=4, google_conversion_rate_high=8,
        google_appointment_cost_multiplier=5,
        meta_ctwa_cpl_low=220, meta_ctwa_cpl_high=500,
        meta_form_cpl_low=500, meta_form_cpl_high=1100,
        meta_cpql_low=700, meta_cpql_high=1400,
        meta_qualified_rate_low=25, meta_qualified_rate_high=38,
        consultation_fee_low=500, consultation_fee_high=1500,
        avg_treatment_value=3200,
        high_value_treatment="Ongoing Psychiatric Care (12mo)", high_value_treatment_cost=38000,
        patient_consideration_days=10,
        repeat_visit_rate=80, lifetime_value_months=12,
        recommended_daily_budget_low=350, recommended_daily_budget_high=800,
        recommended_geo_radius_km=10,
        peak_search_hours=[10, 11, 14, 15, 20, 21, 22, 23],
        peak_search_days=[0, 1, 2, 3, 4, 5, 6],
        top_keywords=["psychiatrist near me", "neurologist near me", "anxiety treatment {city}", "depression doctor", "migraine specialist", "ADHD doctor {city}", "therapist near me"],
        negative_keywords=["psychiatry course", "psychiatrist salary", "mental health tips", "meditation"],
        reel_topics=["Anxiety vs normal worry — when to see a doctor", "Migraine triggers you don't know about", "ADHD in adults — signs you're missing"],
        patient_questions=["Is the consultation confidential?", "Do I need medication?", "How long will treatment take?", "Can I do online consultation?"],
        banned_claims=["guaranteed cure", "best psychiatrist", "no medication needed guaranteed"],
    ),

    Specialty.PHYSIOTHERAPY: SpecialtyBenchmark(
        specialty=Specialty.PHYSIOTHERAPY,
        google_cpc_low=20, google_cpc_high=65,
        google_cpl_low=120, google_cpl_high=350,
        google_cpql_top_quartile=250, google_cpql_market_median=500,
        google_conversion_rate_low=8, google_conversion_rate_high=14,
        google_appointment_cost_multiplier=3,
        meta_ctwa_cpl_low=150, meta_ctwa_cpl_high=300,
        meta_form_cpl_low=300, meta_form_cpl_high=600,
        meta_cpql_low=400, meta_cpql_high=700,
        meta_qualified_rate_low=35, meta_qualified_rate_high=50,
        consultation_fee_low=200, consultation_fee_high=500,
        avg_treatment_value=4500,
        high_value_treatment="Post-Surgery Rehab (12 sessions)", high_value_treatment_cost=15000,
        patient_consideration_days=2,
        repeat_visit_rate=60, lifetime_value_months=6,
        recommended_daily_budget_low=200, recommended_daily_budget_high=500,
        recommended_geo_radius_km=5,
        peak_search_hours=[7, 8, 9, 10, 17, 18, 19, 20],
        peak_search_days=[0, 1, 2, 3, 4, 5],
        top_keywords=["physiotherapy near me", "back pain treatment {city}", "knee pain physiotherapy", "sports injury rehab", "neck pain treatment", "physiotherapist near me"],
        negative_keywords=["physiotherapy course", "BPT admission", "physiotherapist salary", "home exercise"],
        reel_topics=["3 exercises for back pain (do these NOW)", "When to see a physio vs orthopedic", "Post-surgery rehab — timeline explained"],
        patient_questions=["How many sessions will I need?", "How much per session?", "Do you do home visits?", "Can physio replace surgery?"],
        banned_claims=["guaranteed pain relief", "best physiotherapist", "cure without surgery guaranteed"],
    ),

    Specialty.AYURVEDA: SpecialtyBenchmark(
        specialty=Specialty.AYURVEDA,
        google_cpc_low=15, google_cpc_high=55,
        google_cpl_low=100, google_cpl_high=350,
        google_cpql_top_quartile=200, google_cpql_market_median=450,
        google_conversion_rate_low=7, google_conversion_rate_high=13,
        google_appointment_cost_multiplier=3,
        meta_ctwa_cpl_low=120, meta_ctwa_cpl_high=280,
        meta_form_cpl_low=280, meta_form_cpl_high=550,
        meta_cpql_low=350, meta_cpql_high=650,
        meta_qualified_rate_low=35, meta_qualified_rate_high=50,
        consultation_fee_low=200, consultation_fee_high=500,
        avg_treatment_value=8000,
        high_value_treatment="Panchakarma Package", high_value_treatment_cost=15000,
        patient_consideration_days=7,
        repeat_visit_rate=50, lifetime_value_months=12,
        recommended_daily_budget_low=200, recommended_daily_budget_high=500,
        recommended_geo_radius_km=10,
        peak_search_hours=[8, 9, 10, 14, 15, 20, 21],
        peak_search_days=[0, 1, 2, 3, 4, 5, 6],
        top_keywords=["ayurvedic doctor near me", "panchakarma {city}", "ayurvedic treatment {city}", "ayurveda for weight loss", "ayurvedic hair treatment", "ayurvedic skin treatment"],
        negative_keywords=["BAMS course", "ayurveda course", "ayurveda college", "home remedy ayurveda"],
        reel_topics=["Panchakarma — what happens in a 7-day detox", "Ayurveda for weight loss — does it work?", "Modern medicine vs Ayurveda — can they work together?"],
        patient_questions=["How long is the Panchakarma treatment?", "How much does it cost?", "Can Ayurveda treat my condition?", "Are there side effects?"],
        banned_claims=["guaranteed cure", "best ayurvedic doctor", "no side effects guaranteed", "cure cancer/diabetes"],
    ),
}


# ---------------------------------------------------------------------------
# City tier cost adjustments
# ---------------------------------------------------------------------------

CITY_TIER_MULTIPLIER = {
    CityTier.TIER_1: 1.0,     # Base cost (Mumbai, Delhi, Bangalore, etc.)
    CityTier.TIER_2: 0.65,    # 30-50% cheaper than Tier 1
    CityTier.TIER_3: 0.40,    # 50-70% cheaper than Tier 1
}

CITY_TO_TIER = {
    # Tier 1
    "mumbai": CityTier.TIER_1, "delhi": CityTier.TIER_1, "bangalore": CityTier.TIER_1,
    "chennai": CityTier.TIER_1, "hyderabad": CityTier.TIER_1, "kolkata": CityTier.TIER_1,
    "new delhi": CityTier.TIER_1, "bengaluru": CityTier.TIER_1, "noida": CityTier.TIER_1,
    "gurgaon": CityTier.TIER_1, "gurugram": CityTier.TIER_1,
    # Tier 2
    "pune": CityTier.TIER_2, "ahmedabad": CityTier.TIER_2, "jaipur": CityTier.TIER_2,
    "chandigarh": CityTier.TIER_2, "lucknow": CityTier.TIER_2, "indore": CityTier.TIER_2,
    "kochi": CityTier.TIER_2, "nagpur": CityTier.TIER_2, "bhopal": CityTier.TIER_2,
    "surat": CityTier.TIER_2, "vadodara": CityTier.TIER_2, "coimbatore": CityTier.TIER_2,
    "thiruvananthapuram": CityTier.TIER_2, "visakhapatnam": CityTier.TIER_2,
    "patna": CityTier.TIER_2, "ranchi": CityTier.TIER_2, "dehradun": CityTier.TIER_2,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class AIKnowledgeBase:
    """
    Central knowledge base that all PatientPlex AI services query.

    Usage:
        kb = AIKnowledgeBase()

        # Get benchmark for a specialty
        dental = kb.get_benchmark(Specialty.DENTAL_GENERAL)

        # Get city-adjusted CPC
        cpc = kb.get_adjusted_cpc(Specialty.DENTAL_GENERAL, "pune")

        # Get campaign template
        template = kb.get_campaign_template(Specialty.DENTAL_GENERAL, "hyderabad", 15000)

        # Get AI receptionist knowledge
        knowledge = kb.get_receptionist_knowledge(Specialty.DENTAL_GENERAL)

        # Get content calendar
        calendar = kb.get_content_calendar(Specialty.DENTAL_GENERAL, "mumbai")
    """

    def __init__(self):
        self.benchmarks = SPECIALTY_BENCHMARKS
        self.city_tiers = CITY_TO_TIER
        self.tier_multipliers = CITY_TIER_MULTIPLIER

    def get_benchmark(self, specialty: Specialty) -> SpecialtyBenchmark:
        """Get full benchmark data for a specialty."""
        return self.benchmarks[specialty]

    def get_city_tier(self, city: str) -> CityTier:
        """Determine city tier. Defaults to Tier 3 for unknown cities."""
        return self.city_tiers.get(city.lower().strip(), CityTier.TIER_3)

    def get_adjusted_cpc(self, specialty: Specialty, city: str) -> Tuple[float, float]:
        """Get city-adjusted CPC range for a specialty."""
        bm = self.benchmarks[specialty]
        tier = self.get_city_tier(city)
        mult = self.tier_multipliers[tier]
        return (bm.google_cpc_low * mult, bm.google_cpc_high * mult)

    def get_adjusted_cpl(self, specialty: Specialty, city: str) -> Tuple[float, float]:
        """Get city-adjusted CPL range for a specialty."""
        bm = self.benchmarks[specialty]
        tier = self.get_city_tier(city)
        mult = self.tier_multipliers[tier]
        return (bm.google_cpl_low * mult, bm.google_cpl_high * mult)

    def get_campaign_template(self, specialty: Specialty, city: str, monthly_budget: float) -> Dict:
        """Generate a complete campaign template for a clinic."""
        bm = self.benchmarks[specialty]
        tier = self.get_city_tier(city)
        mult = self.tier_multipliers[tier]

        daily_budget = monthly_budget / 30
        adj_cpc_avg = ((bm.google_cpc_low + bm.google_cpc_high) / 2) * mult
        est_clicks_day = daily_budget / adj_cpc_avg
        est_conv_rate = (bm.google_conversion_rate_low + bm.google_conversion_rate_high) / 2 / 100
        est_leads_day = est_clicks_day * est_conv_rate
        est_leads_month = est_leads_day * 30

        keywords_with_city = [kw.replace("{city}", city.title()) for kw in bm.top_keywords]

        return {
            "specialty": specialty.value,
            "city": city.title(),
            "city_tier": tier.value,
            "monthly_budget": monthly_budget,
            "daily_budget": round(daily_budget),
            "estimated_avg_cpc": round(adj_cpc_avg),
            "estimated_clicks_per_day": round(est_clicks_day, 1),
            "estimated_leads_per_day": round(est_leads_day, 1),
            "estimated_leads_per_month": round(est_leads_month),
            "estimated_cpl": round(monthly_budget / est_leads_month) if est_leads_month > 0 else 0,
            "target_conversion_rate": f"{bm.google_conversion_rate_low}-{bm.google_conversion_rate_high}%",
            "geo_radius_km": bm.recommended_geo_radius_km,
            "peak_hours": bm.peak_search_hours,
            "peak_days": bm.peak_search_days,
            "keywords": keywords_with_city,
            "negative_keywords": bm.negative_keywords,
            "ad_copy_guidelines": {
                "banned_claims": bm.banned_claims,
                "avg_treatment_value": bm.avg_treatment_value,
                "consultation_fee_range": f"₹{int(bm.consultation_fee_low)}-{int(bm.consultation_fee_high)}",
            },
            "expected_roas": round(bm.avg_treatment_value / (monthly_budget / est_leads_month * bm.google_appointment_cost_multiplier), 1) if est_leads_month > 0 else 0,
        }

    def get_receptionist_knowledge(self, specialty: Specialty) -> Dict:
        """Get AI receptionist knowledge for a specialty — what to say, what NOT to say."""
        bm = self.benchmarks[specialty]
        return {
            "specialty": specialty.value,
            "consultation_fee_range": f"₹{int(bm.consultation_fee_low)}-{int(bm.consultation_fee_high)}",
            "common_treatments": bm.top_keywords[:5],
            "patient_faqs": bm.patient_questions,
            "banned_claims": bm.banned_claims,
            "high_value_treatment": bm.high_value_treatment,
            "high_value_cost": bm.high_value_treatment_cost,
            "consideration_period_days": bm.patient_consideration_days,
            "follow_up_schedule": _get_follow_up_schedule(bm.patient_consideration_days),
            "response_rules": [
                "NEVER give medical advice — only book appointments",
                "NEVER diagnose conditions — say 'Please visit the doctor for clinical guidance'",
                "ALWAYS check calendar before confirming a slot",
                "ALWAYS send confirmation message with date, time, address",
                "ALWAYS follow up if patient doesn't respond in 4 hours",
                "For pricing, give range: 'Treatment starts from ₹X. Final cost discussed during consultation.'",
                f"For {bm.high_value_treatment}: mention EMI/payment plan availability",
            ],
        }

    def get_content_calendar(self, specialty: Specialty, city: str) -> Dict:
        """Generate monthly content calendar for a clinic."""
        bm = self.benchmarks[specialty]
        topics_with_city = [t.replace("{city}", city.title()) for t in bm.reel_topics]

        return {
            "specialty": specialty.value,
            "city": city.title(),
            "reels_per_month": 12,
            "reel_topics": topics_with_city,
            "blog_topics": [f"Best {specialty.value.replace('_', ' ')} treatments in {city.title()} — Complete Guide 2026"],
            "gmb_posts_per_month": 4,
            "whatsapp_broadcasts_per_month": 6,
            "meta_ad_budget_split": {
                "awareness_reels": "30%",
                "ctwa_lead_gen": "45%",
                "retargeting": "20%",
                "lookalike": "5%",
            },
        }

    def get_all_specialties(self) -> List[Dict]:
        """Return summary of all specialties for dropdown/selection."""
        result = []
        for spec, bm in self.benchmarks.items():
            result.append({
                "specialty": spec.value,
                "display_name": spec.value.replace("_", " ").title(),
                "avg_treatment_value": bm.avg_treatment_value,
                "google_cpl_range": f"₹{int(bm.google_cpl_low)}-{int(bm.google_cpl_high)}",
                "meta_ctwa_cpl_range": f"₹{int(bm.meta_ctwa_cpl_low)}-{int(bm.meta_ctwa_cpl_high)}",
                "recommended_budget": f"₹{int(bm.recommended_daily_budget_low * 30)}-{int(bm.recommended_daily_budget_high * 30)}/month",
            })
        return result

    def estimate_roi(self, specialty: Specialty, city: str, monthly_budget: float) -> Dict:
        """Estimate ROI for a clinic based on specialty, city, and budget."""
        template = self.get_campaign_template(specialty, city, monthly_budget)
        bm = self.benchmarks[specialty]
        booking_rate = 0.43  # 43% lead→booking (from our AI receptionist data)
        attendance_rate = 0.84  # 84% booking→attendance

        est_bookings = template["estimated_leads_per_month"] * booking_rate
        est_patients = est_bookings * attendance_rate
        est_revenue = est_patients * bm.avg_treatment_value

        return {
            **template,
            "estimated_bookings_per_month": round(est_bookings, 1),
            "estimated_patients_per_month": round(est_patients, 1),
            "estimated_revenue": round(est_revenue),
            "estimated_roas": round(est_revenue / monthly_budget, 1) if monthly_budget > 0 else 0,
            "cost_per_patient": round(monthly_budget / est_patients) if est_patients > 0 else 0,
            "avg_treatment_value": bm.avg_treatment_value,
        }


def _get_follow_up_schedule(consideration_days: int) -> List[Dict]:
    """Generate follow-up schedule based on patient consideration period."""
    if consideration_days <= 3:
        return [
            {"delay_hours": 4, "message": "reminder_1", "channel": "whatsapp"},
            {"delay_hours": 24, "message": "reminder_2", "channel": "whatsapp"},
            {"delay_hours": 72, "message": "final_reminder", "channel": "whatsapp"},
        ]
    elif consideration_days <= 14:
        return [
            {"delay_hours": 4, "message": "reminder_1", "channel": "whatsapp"},
            {"delay_hours": 48, "message": "reminder_2", "channel": "whatsapp"},
            {"delay_hours": 168, "message": "info_share", "channel": "whatsapp"},
            {"delay_hours": 336, "message": "final_reminder", "channel": "whatsapp"},
        ]
    else:  # Long consideration (IVF, cosmetic surgery)
        return [
            {"delay_hours": 4, "message": "reminder_1", "channel": "whatsapp"},
            {"delay_hours": 48, "message": "info_brochure", "channel": "whatsapp"},
            {"delay_hours": 168, "message": "success_stories", "channel": "whatsapp"},
            {"delay_hours": 336, "message": "consultation_offer", "channel": "whatsapp"},
            {"delay_hours": 672, "message": "check_in", "channel": "whatsapp"},
            {"delay_hours": 1008, "message": "final_reminder", "channel": "whatsapp"},
        ]


# Singleton instance
knowledge_base = AIKnowledgeBase()
