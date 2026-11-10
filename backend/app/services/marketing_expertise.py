"""
PatientPlex Marketing Expertise Module — Performance marketing knowledge
fed into the AI to make optimization decisions.

This is what a ₹2L/month healthcare performance marketing specialist knows,
encoded as rules and heuristics for our AI to apply automatically.

Sources:
- ICG (India's largest healthcare ad agency) published playbooks
- HealthcareSuccess 20-point optimization guide
- ClickMaking India healthcare funnel guide
- 10+ years of Google Ads best practices
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Google Ads Optimization Rules
# ---------------------------------------------------------------------------

QUALITY_SCORE_RULES = [
    {
        "rule": "keyword_in_headline",
        "description": "Primary keyword MUST appear in at least 1 of 3 RSA headlines",
        "impact": "Quality Score +1-2 points",
        "implementation": "When generating ad copy, extract primary keyword from ad group and include verbatim in headline 1 or 2",
    },
    {
        "rule": "keyword_in_description",
        "description": "Primary keyword should appear in at least 1 of 2 RSA descriptions",
        "impact": "Quality Score +0.5-1 point",
        "implementation": "Include keyword naturally in description line 1",
    },
    {
        "rule": "landing_page_relevance",
        "description": "Landing page must contain the exact keyword, city name, and specialty",
        "impact": "Quality Score +1-2 points, also improves conversion rate",
        "implementation": "Generate dynamic landing pages with {keyword} and {city} in H1, H2, and body text",
    },
    {
        "rule": "landing_page_speed",
        "description": "Landing page LCP must be under 2.5 seconds",
        "impact": "Quality Score +0.5-1 point. ICG case: LCP 4.8s → 1.9s improved QS by 2 points",
        "implementation": "Use lightweight pages, optimize images, lazy load below-fold content",
    },
    {
        "rule": "ctr_improvement",
        "description": "CTR above industry average improves Quality Score. Healthcare avg is 3.27%",
        "impact": "Every 1% CTR above average = ~0.5 QS improvement",
        "implementation": "Use emotional triggers, urgency, price anchoring in ad copy. Add all extensions.",
    },
    {
        "rule": "ad_extensions",
        "description": "Always use: sitelinks (4+), callouts (4+), structured snippets, location, call extension",
        "impact": "CTR +10-20%, Quality Score improvement",
        "implementation": "Auto-generate extensions from specialty knowledge base",
    },
]

BIDDING_STRATEGIES = {
    "new_campaign_0_30_days": {
        "strategy": "Manual CPC with Enhanced",
        "reason": "Need data before smart bidding. Collect 30+ conversions first.",
        "initial_bid": "Set at 70% of specialty avg CPC to avoid overspend",
        "adjustments": {
            "mobile": "+20% (healthcare searches are 60%+ mobile in India)",
            "peak_hours": "+30% during specialty peak hours",
            "off_hours": "-40% during midnight-6am (except emergency keywords)",
            "weekends": "+10% for dental/derma, -20% for corporate specialties",
        },
    },
    "established_30_90_days": {
        "strategy": "Target CPA (tCPA)",
        "reason": "Enough conversion data. Set target CPA at 120% of current average.",
        "optimization": "Reduce tCPA by 5% every 2 weeks if achieving target consistently",
        "fallback": "Switch back to Manual CPC if conversions drop >30% week-over-week",
    },
    "mature_90_plus_days": {
        "strategy": "Target ROAS (tROAS) if conversion values tracked, else Maximize Conversions",
        "reason": "Full data set. Optimize for revenue, not just leads.",
        "target_roas": "Set at 80% of current ROAS to allow algorithm room",
    },
}

NEGATIVE_KEYWORD_MASTER_LIST = {
    "universal_healthcare": [
        # Job seekers
        "job", "jobs", "vacancy", "career", "salary", "hiring", "recruitment",
        "resume", "interview", "internship", "fresher",
        # Education
        "course", "college", "university", "admission", "syllabus", "exam",
        "MBBS", "BDS", "MD", "MS", "BAMS", "BHMS", "BPT", "degree",
        "training", "certification", "diploma",
        # DIY / Home remedies
        "home remedy", "home remedies", "natural cure", "ayurvedic remedy",
        "gharelu nuskha", "desi ilaj", "DIY",
        # Research / Information
        "wikipedia", "definition", "meaning", "vs", "comparison",
        "research paper", "journal", "study", "statistics",
        # Insurance / Legal
        "insurance claim", "medical negligence", "malpractice",
        "complaint against doctor",
        # Free / Discount (unless running offer campaigns)
        "free treatment", "government hospital", "sarkari hospital",
        "free clinic", "NGO",
        # Irrelevant locations
        "USA", "UK", "Dubai", "abroad", "overseas",
    ],
    "dental_specific": [
        "dental college admission", "BDS admission", "dental assistant",
        "dental hygienist", "dental material", "dental instruments",
        "dental lab", "dental supplier", "toothpaste review",
        "electric toothbrush", "dental insurance",
    ],
    "dermatology_specific": [
        "dermatology course", "skin care routine DIY", "homemade face pack",
        "beauty tips", "makeup tutorial", "dermatologist salary",
    ],
    "ivf_specific": [
        "IVF training", "embryologist course", "IVF failure stories",
        "IVF risks death", "IVF alternatives natural", "adopt baby",
    ],
    "hair_transplant_specific": [
        "hair transplant training", "hair transplant course",
        "hair transplant gone wrong", "hair transplant failure",
        "hair oil", "shampoo for hair loss", "minoxidil DIY",
    ],
}

CAMPAIGN_STRUCTURE_TEMPLATE = {
    "account_level": {
        "conversion_tracking": "Primary: Phone calls (30s+) + WhatsApp clicks + Form submissions",
        "enhanced_conversions": "MANDATORY — hashed email/phone for better attribution",
        "attribution_model": "Data-driven (if enough data) or Position-based",
        "audience_signals": "Upload patient list for similar audiences",
    },
    "campaign_structure": {
        "campaign_1_brand": {
            "name": "{clinic_name} — Brand",
            "type": "Search",
            "budget": "5-10% of total",
            "keywords": "Clinic name, doctor name, brand terms",
            "reason": "Protect brand from competitors bidding on your name",
        },
        "campaign_2_core_treatments": {
            "name": "{specialty} — Core Treatments",
            "type": "Search",
            "budget": "50-60% of total",
            "keywords": "Treatment + city keywords (root canal mumbai, dental implant cost hyderabad)",
            "reason": "Highest intent, highest conversion. This is where money is made.",
        },
        "campaign_3_near_me": {
            "name": "{specialty} — Near Me / Local",
            "type": "Search",
            "budget": "25-30% of total",
            "keywords": "dentist near me, dental clinic near me, {specialty} doctor near me",
            "reason": "High volume, moderate intent. Good for new patient acquisition.",
        },
        "campaign_4_competitor": {
            "name": "{specialty} — Competitor",
            "type": "Search",
            "budget": "5-10% of total",
            "keywords": "Competitor clinic names (if legally allowed)",
            "reason": "Steal patients from competitors. Use carefully — high CPC, low QS.",
        },
    },
    "ad_group_structure": {
        "rule": "One ad group per treatment/service",
        "example": {
            "dental": [
                "Root Canal", "Dental Implant", "Braces/Aligners",
                "Teeth Whitening", "Teeth Cleaning", "Wisdom Tooth",
                "Emergency Dental", "Cosmetic Dentistry",
            ],
        },
        "reason": "Tighter keyword→ad→landing page match = higher Quality Score = lower CPC",
    },
}

AD_COPY_FORMULAS = {
    "headline_formulas": [
        "{Treatment} in {City} — Book Now",
        "{Treatment} Starting ₹{Price} | {Clinic}",
        "Expert {Specialty} in {City} | {USP}",
        "₹{Price} {Treatment} | {Clinic} {City}",
        "{City}'s Trusted {Specialty} | Book Today",
        "Same Day {Treatment} Available | {Clinic}",
        "0% EMI on {Treatment} | {Clinic}",
    ],
    "description_formulas": [
        "Experienced {specialty} with {years}+ years. Advanced technology. Book your consultation today. Walk-ins welcome.",
        "{Treatment} starting from ₹{price}. {Clinic} in {area}, {city}. Open 7 days. Call or WhatsApp now.",
        "Trusted by {patient_count}+ patients. NMC-registered. {USP}. Book appointment — instant WhatsApp confirmation.",
    ],
    "nmc_compliance_rules": [
        "NEVER use: best, number 1, guaranteed, cheapest, top, leading",
        "NEVER use patient testimonials in ad copy",
        "NEVER show before/after photos in Google Ads (NMC Oct 2026 rule)",
        "NEVER claim specific success rates without published evidence",
        "NEVER use 'Dr.' prefix without the actual registered doctor's name",
        "OK to use: experienced, trusted, advanced, modern, affordable, transparent pricing",
        "OK to mention: EMI options, insurance acceptance, clinic timings, location",
    ],
}

SEARCH_TERM_OPTIMIZATION = {
    "weekly_review_process": [
        "1. Pull Search Terms Report for last 7 days",
        "2. Sort by Cost (highest first) — find expensive irrelevant terms",
        "3. Add irrelevant terms as exact-match negatives",
        "4. Find high-converting search terms not in keyword list — add as keywords",
        "5. Check for competitor brand terms — decide: bid or negative",
        "6. Check for location-based terms outside geo-target — add as negatives",
        "7. Review 'near me' variants — ensure location extensions are active",
    ],
    "auto_rules": [
        {
            "rule": "pause_bleeder_keywords",
            "condition": "Keyword spend > ₹500 AND conversions = 0 in last 14 days",
            "action": "Auto-pause keyword, flag for human review",
        },
        {
            "rule": "boost_winner_keywords",
            "condition": "Keyword CPA < target CPA AND conversions >= 3 in last 7 days",
            "action": "Increase bid by 15%",
        },
        {
            "rule": "budget_pacing",
            "condition": "Daily spend < 80% of daily budget by 2pm",
            "action": "Increase bids by 10% for remaining hours",
        },
        {
            "rule": "budget_protection",
            "condition": "Daily spend > 110% of daily budget",
            "action": "Reduce bids by 20%, alert clinic owner",
        },
        {
            "rule": "quality_score_alert",
            "condition": "Quality Score drops below 5 for any keyword with >50 impressions",
            "action": "Flag for ad copy + landing page review",
        },
    ],
}

META_ADS_EXPERTISE = {
    "ctwa_best_practices": [
        "Use Click-to-WhatsApp (CTWA) — 67% of healthcare Meta leads in India 2026",
        "CTWA CPL is 40-60% cheaper than Form CPL for healthcare",
        "Set up WhatsApp Business API (not personal) for CTWA ads",
        "Auto-greet message must fire within 3 seconds of WhatsApp open",
        "Include: clinic name, treatment enquired about, consultation offer",
        "Follow-up within 4 hours if patient doesn't respond to first message",
    ],
    "creative_strategy": {
        "format_priority": ["Reels (9:16 video)", "Carousel", "Single image", "Story"],
        "video_length": "15-30 seconds for awareness, 30-60 seconds for consideration",
        "hook_in_first_3_seconds": True,
        "captions_required": True,  # 85% of Meta video is watched without sound
        "creative_refresh": "Every 2-3 weeks — fatigue kills CTR",
        "ugc_vs_polished": "UGC (doctor talking to camera) outperforms polished studio content by 2-3x in healthcare",
    },
    "audience_targeting": {
        "interest_based": "Healthcare, specific treatments, competitor pages, related conditions",
        "lookalike": "1-3% lookalike from patient list (phone numbers) — best performing",
        "retargeting": "Website visitors + video viewers (75%+ completion) — highest ROAS",
        "exclusions": "Exclude existing patients, competitors' employees, medical professionals",
    },
    "budget_allocation": {
        "awareness_reels": "30% — broad reach, video views objective",
        "ctwa_lead_gen": "45% — primary lead engine",
        "retargeting": "20% — highest ROAS, warm audience",
        "testing": "5% — new creatives, new audiences",
    },
}

WHATSAPP_NURTURE_SEQUENCES = {
    "dental_general": {
        "day_0_hour_0": "Hi {name}! Thanks for your interest in {treatment} at {clinic}. Our consultation fee is ₹{fee}. Would you like to book? We have slots available {next_slots}.",
        "day_0_hour_4": "Hi {name}, just checking — would you like to book your {treatment} consultation? We have slots tomorrow at {time1} and {time2}. 😊",
        "day_1": "Hi {name}! Quick reminder — Dr. {doctor} at {clinic} is available for your {treatment} consultation. Shall I book you in?",
        "day_3": "Hi {name}, many patients ask about {treatment} cost. At {clinic}, {treatment} starts from ₹{price}. Book a consultation to get your personalized treatment plan. Would {day} work for you?",
    },
    "ivf_fertility": {
        "day_0_hour_0": "Hello {name}. Thank you for reaching out about fertility consultation at {clinic}. We understand this is an important step. Dr. {doctor} is available for a confidential consultation. Would you like to know more about the process?",
        "day_0_hour_4": "Hi {name}, if you have any questions about IVF or fertility treatments, feel free to ask. We're here to help. 💙",
        "day_2": "Hi {name}, many patients find it helpful to know what to expect. Here's a brief overview of the IVF process at {clinic}: [info link]. Would you like to schedule a consultation?",
        "day_7": "Hi {name}, Dr. {doctor} has helped {count}+ couples on their journey to parenthood. A consultation is the first step — no commitment. We also offer 0% EMI payment plans. Would you like to book?",
        "day_14": "Hi {name}, just checking in. If you're still considering fertility treatment, Dr. {doctor} has limited slots this month. We offer a free initial assessment. Would you like to know more?",
    },
    "hair_transplant": {
        "day_0_hour_0": "Hi {name}! Thanks for your interest in hair transplant at {clinic}. Our FUE procedure starts from ₹{price} per graft. Would you like to book a free consultation?",
        "day_0_hour_4": "Hi {name}, our hair transplant specialist can assess your case and give you an exact quote. The consultation is free and takes about 15 minutes. Shall I book?",
        "day_3": "Hi {name}, here are some results from our recent patients: [before/after link — NMC compliant, with consent]. Every case is different — a consultation will help us understand yours. Book today?",
        "day_7": "Hi {name}, quick update — Dr. {doctor} has surgery slots opening next month. If you'd like to proceed, the first step is a consultation (free). We also offer 0% EMI up to 12 months.",
        "day_14": "Hi {name}, still thinking about hair restoration? That's completely normal — it's a big decision. If you have any questions, just reply here. We're happy to help. 😊",
    },
}

PERFORMANCE_MARKETER_DAILY_CHECKLIST = [
    "☐ Check all accounts: any overspend alerts?",
    "☐ Check conversion tracking: any accounts with 0 conversions in 24h?",
    "☐ Review Search Terms Report for top 10 spending accounts",
    "☐ Check Quality Scores: any dropped below 5?",
    "☐ Check ad disapprovals: any new NMC/Google policy rejections?",
    "☐ Review WhatsApp response rate: any accounts below 80%?",
    "☐ Check budget pacing: any accounts exhausting budget before 6pm?",
    "☐ Review landing page uptime: all pages loading under 3 seconds?",
    "☐ Check competitor activity: any new competitor ads in top positions?",
    "☐ Update CRM: mark new leads, update conversion status",
]


class MarketingExpertise:
    """
    Provides performance marketing expertise to the AI optimizer.

    Usage:
        expert = MarketingExpertise()

        # Get campaign structure for a new clinic
        structure = expert.get_campaign_structure("dental_general", "mumbai", 15000)

        # Get ad copy recommendations
        copies = expert.generate_ad_copies("dental_general", "mumbai", "Root Canal")

        # Get optimization recommendations
        recommendations = expert.get_optimization_actions(campaign_metrics)

        # Get negative keywords for a specialty
        negatives = expert.get_negative_keywords("dental_general")
    """

    def get_campaign_structure(self, specialty: str, city: str, monthly_budget: float) -> Dict:
        """Return recommended campaign structure for a clinic."""
        return {
            **CAMPAIGN_STRUCTURE_TEMPLATE,
            "specialty": specialty,
            "city": city,
            "monthly_budget": monthly_budget,
            "budget_split": {
                "brand": round(monthly_budget * 0.075),
                "core_treatments": round(monthly_budget * 0.55),
                "near_me_local": round(monthly_budget * 0.275),
                "competitor": round(monthly_budget * 0.10),
            },
        }

    def get_negative_keywords(self, specialty: str) -> List[str]:
        """Get merged negative keyword list for a specialty."""
        negatives = list(NEGATIVE_KEYWORD_MASTER_LIST["universal_healthcare"])
        specialty_key = f"{specialty}_specific"
        if specialty_key in NEGATIVE_KEYWORD_MASTER_LIST:
            negatives.extend(NEGATIVE_KEYWORD_MASTER_LIST[specialty_key])
        return negatives

    def get_bidding_strategy(self, campaign_age_days: int, total_conversions: int) -> Dict:
        """Recommend bidding strategy based on campaign maturity."""
        if campaign_age_days < 30 or total_conversions < 30:
            return BIDDING_STRATEGIES["new_campaign_0_30_days"]
        elif campaign_age_days < 90:
            return BIDDING_STRATEGIES["established_30_90_days"]
        else:
            return BIDDING_STRATEGIES["mature_90_plus_days"]

    def get_auto_rules(self) -> List[Dict]:
        """Get automated optimization rules."""
        return SEARCH_TERM_OPTIMIZATION["auto_rules"]

    def get_ad_copy_formulas(self) -> Dict:
        """Get ad copy generation templates and NMC compliance rules."""
        return AD_COPY_FORMULAS

    def get_meta_ads_expertise(self) -> Dict:
        """Get Meta/Facebook/Instagram Ads best practices."""
        return META_ADS_EXPERTISE

    def get_nurture_sequence(self, specialty: str) -> Dict:
        """Get WhatsApp nurture message templates for a specialty."""
        key = specialty.replace(" ", "_").lower()
        return WHATSAPP_NURTURE_SEQUENCES.get(key, WHATSAPP_NURTURE_SEQUENCES["dental_general"])

    def get_daily_checklist(self) -> List[str]:
        """Get the performance marketer's daily optimization checklist."""
        return PERFORMANCE_MARKETER_DAILY_CHECKLIST

    def evaluate_campaign_health(self, metrics: Dict) -> Dict:
        """Evaluate a campaign's health and suggest actions."""
        issues = []
        actions = []

        ctr = metrics.get("ctr", 0)
        cpc = metrics.get("avg_cpc", 0)
        conv_rate = metrics.get("conversion_rate", 0)
        quality_score = metrics.get("avg_quality_score", 0)
        spend = metrics.get("total_spend", 0)
        conversions = metrics.get("conversions", 0)

        # CTR check
        if ctr < 3.0:
            issues.append({"metric": "CTR", "value": f"{ctr}%", "severity": "HIGH", "issue": "CTR below healthcare average (3.27%)"})
            actions.append("Rewrite ad copy with stronger hooks and CTAs")
            actions.append("Add all ad extensions (sitelinks, callouts, location)")
            actions.append("Review search terms — may be matching irrelevant queries")

        # Quality Score check
        if quality_score < 5:
            issues.append({"metric": "Quality Score", "value": str(quality_score), "severity": "CRITICAL", "issue": "Quality Score too low — paying premium CPC"})
            actions.append("Match keyword in ad headline and description")
            actions.append("Improve landing page relevance and speed")
            actions.append("Add more relevant keywords, pause irrelevant ones")

        # Conversion rate check
        if conv_rate < 3:
            issues.append({"metric": "Conversion Rate", "value": f"{conv_rate}%", "severity": "HIGH", "issue": "Landing page not converting"})
            actions.append("Review landing page — is CTA clear? Is WhatsApp button prominent?")
            actions.append("Check page speed — must be under 2.5 seconds")
            actions.append("Ensure phone number and WhatsApp are clickable on mobile")

        # Spend efficiency
        if spend > 0 and conversions == 0 and spend > 500:
            issues.append({"metric": "Conversions", "value": "0", "severity": "CRITICAL", "issue": f"₹{spend} spent with zero conversions"})
            actions.append("PAUSE campaign immediately — diagnose before resuming")
            actions.append("Check: is conversion tracking firing? Test with a real click.")
            actions.append("Check: is the landing page loading? Is the WhatsApp CTA working?")

        health_score = 100
        for issue in issues:
            if issue["severity"] == "CRITICAL":
                health_score -= 30
            elif issue["severity"] == "HIGH":
                health_score -= 15
            else:
                health_score -= 5

        return {
            "health_score": max(0, health_score),
            "status": "HEALTHY" if health_score >= 70 else "NEEDS ATTENTION" if health_score >= 40 else "CRITICAL",
            "issues": issues,
            "recommended_actions": actions,
        }


# Singleton
marketing_expertise = MarketingExpertise()
