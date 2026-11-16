"""
Keyword Intelligence — Real search volume, CPC, and competition data
for Indian healthcare professions across major cities.

Data source: Master Keyword Sheet (City × Pincode × Profession)
This feeds the Performance Marketing Brain with actual market data
so it can make real decisions about which campaigns to create,
what budgets to set, and which keywords to target.

Cities covered: Hyderabad, Indore, Mumbai, Delhi NCR, Bangalore, Chennai, Bhopal
Professions: Dermatologist, Skin Specialist, Dentist, Dental Clinic,
             Gynecologist, Orthopedic, Physiotherapist, Hair Transplant
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class KeywordData:
    """Real search data for a keyword."""
    keyword: str
    keyword_level: str  # "City Head Term" or "Locality Long-Tail"
    search_volume_monthly: int
    cpc_usd: float
    competition_score: float  # 0-1
    keyword_difficulty: int   # 0-100
    priority_tier: str        # "Tier 1 - Head", "Tier 2 - Strong", etc.


@dataclass
class CityProfessionData:
    """Market data for a profession in a specific city."""
    city: str
    profession: str
    specialty_group: str
    city_head_term: KeywordData
    locality_keywords: list[KeywordData]
    total_search_volume: int
    avg_cpc_usd: float
    avg_competition: float


# ═══════════════════════════════════════════════════════════════
# REAL MARKET DATA — Extracted from Master Keyword Sheet
# City-wide Head Terms (highest volume, most competitive)
# ═══════════════════════════════════════════════════════════════

CITY_HEAD_TERMS: dict[str, dict[str, KeywordData]] = {
    # ── HYDERABAD ──
    "hyderabad": {
        "dermatologist": KeywordData("dermatologist in hyderabad", "City Head Term", 14800, 0.40, 0.45, 35, "Tier 1 - Head"),
        "skin_specialist": KeywordData("skin specialist in hyderabad", "City Head Term", 8100, 0.35, 0.49, 30, "Tier 1 - Head"),
        "dentist": KeywordData("dentist in hyderabad", "City Head Term", 2400, 0.80, 0.38, 28, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in hyderabad", "City Head Term", 2900, 0.78, 0.34, 55, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in hyderabad", "City Head Term", 2900, 0.21, 0.26, 29, "Tier 2 - Strong"),
        "orthopedic": KeywordData("orthopedic doctor in hyderabad", "City Head Term", 6600, 0.26, 0.32, 25, "Tier 1 - Head"),
        "physiotherapist": KeywordData("physiotherapist in hyderabad", "City Head Term", 4400, 0.62, 0.53, 22, "Tier 2 - Strong"),
        "hair_transplant": KeywordData("hair transplant in hyderabad", "City Head Term", 2900, 1.72, 0.62, 17, "Tier 2 - Strong"),
    },
    # ── INDORE ──
    "indore": {
        "dermatologist": KeywordData("dermatologist in indore", "City Head Term", 8100, 0.10, 0.24, 27, "Tier 1 - Head"),
        "skin_specialist": KeywordData("skin specialist in indore", "City Head Term", 5400, 0.09, 0.32, 28, "Tier 1 - Head"),
        "dentist": KeywordData("dentist in indore", "City Head Term", 2900, 0.09, 0.21, 22, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in indore", "City Head Term", 1900, 0.13, 0.23, 21, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in indore", "City Head Term", 5400, 0.12, 0.11, 21, "Tier 1 - Head"),
        "orthopedic": KeywordData("orthopedic doctor in indore", "City Head Term", 1000, 0.06, 0.13, 23, "Tier 2 - Strong"),
        "physiotherapist": KeywordData("physiotherapist in indore", "City Head Term", 2400, 0.09, 0.18, 21, "Tier 2 - Strong"),
        "hair_transplant": KeywordData("hair transplant in indore", "City Head Term", 1300, 0.63, 0.57, 12, "Tier 2 - Strong"),
    },
    # ── MUMBAI ──
    "mumbai": {
        "dermatologist": KeywordData("dermatologist in mumbai", "City Head Term", 8100, 0.25, 0.21, 37, "Tier 1 - Head"),
        "skin_specialist": KeywordData("skin specialist in mumbai", "City Head Term", 5400, 0.28, 0.31, 46, "Tier 1 - Head"),
        "dentist": KeywordData("dentist in mumbai", "City Head Term", 3600, 1.85, 0.25, 43, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in mumbai", "City Head Term", 2400, 1.83, 0.19, 23, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in mumbai", "City Head Term", 880, 0.19, 0.11, 23, "Tier 3 - Viable"),
        "orthopedic": KeywordData("orthopedic doctor in mumbai", "City Head Term", 2900, 0.27, 0.29, 32, "Tier 2 - Strong"),
        "physiotherapist": KeywordData("physiotherapist in mumbai", "City Head Term", 4400, 0.59, 0.37, 29, "Tier 2 - Strong"),
        "hair_transplant": KeywordData("hair transplant in mumbai", "City Head Term", 2900, 1.38, 0.64, 16, "Tier 2 - Strong"),
    },
    # ── DELHI NCR ──
    "delhi": {
        "dermatologist": KeywordData("dermatologist in delhi", "City Head Term", 12100, 0.32, 0.34, 35, "Tier 1 - Head"),
        "skin_specialist": KeywordData("skin specialist in delhi", "City Head Term", 8100, 0.35, 0.49, 30, "Tier 1 - Head"),
        "dentist": KeywordData("dentist in delhi", "City Head Term", 4400, 1.67, 0.27, 40, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in delhi", "City Head Term", 2900, 1.68, 0.24, 48, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in delhi", "City Head Term", 2900, 0.21, 0.35, 28, "Tier 2 - Strong"),
        "orthopedic": KeywordData("orthopedic doctor in delhi", "City Head Term", 1300, 0.27, 0.31, 28, "Tier 2 - Strong"),
        "physiotherapist": KeywordData("physiotherapist in delhi", "City Head Term", 6600, 0.55, 0.32, 27, "Tier 1 - Head"),
        "hair_transplant": KeywordData("hair transplant in delhi", "City Head Term", 4400, 1.40, 0.57, 52, "Tier 2 - Strong"),
    },
    # ── BANGALORE ──
    "bangalore": {
        "dermatologist": KeywordData("dermatologist in bangalore", "City Head Term", 14800, 0.41, 0.42, 30, "Tier 1 - Head"),
        "skin_specialist": KeywordData("skin specialist in bangalore", "City Head Term", 8100, 0.40, 0.47, 33, "Tier 1 - Head"),
        "dentist": KeywordData("dentist in bangalore", "City Head Term", 3600, 0.55, 0.49, 34, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in bangalore", "City Head Term", 3600, 0.53, 0.32, 29, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in bangalore", "City Head Term", 2400, 0.38, 0.39, 30, "Tier 2 - Strong"),
        "orthopedic": KeywordData("orthopedic doctor in bangalore", "City Head Term", 880, 0.47, 0.40, 24, "Tier 3 - Viable"),
        "physiotherapist": KeywordData("physiotherapist in bangalore", "City Head Term", 5400, 0.76, 0.55, 30, "Tier 1 - Head"),
        "hair_transplant": KeywordData("hair transplant in bangalore", "City Head Term", 880, 1.65, 0.74, 16, "Tier 3 - Viable"),
    },
    # ── CHENNAI ──
    "chennai": {
        "dermatologist": KeywordData("dermatologist in chennai", "City Head Term", 22200, 0.38, 0.31, 30, "Tier 1 - Head"),
        "skin_specialist": KeywordData("skin specialist in chennai", "City Head Term", 6600, 0.35, 0.38, 28, "Tier 1 - Head"),
        "dentist": KeywordData("dentist in chennai", "City Head Term", 1900, 0.44, 0.25, 30, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in chennai", "City Head Term", 1600, 0.38, 0.13, 43, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in chennai", "City Head Term", 2900, 0.29, 0.28, 26, "Tier 2 - Strong"),
        "orthopedic": KeywordData("orthopedic doctor in chennai", "City Head Term", 590, 0.30, 0.37, 27, "Tier 3 - Viable"),
        "hair_transplant": KeywordData("hair transplant in chennai", "City Head Term", 1900, 1.60, 0.75, 17, "Tier 2 - Strong"),
    },
    # ── BHOPAL ──
    "bhopal": {
        "dermatologist": KeywordData("dermatologist in bhopal", "City Head Term", 480, 0.08, 0.16, 18, "Tier 3 - Viable"),
        "skin_specialist": KeywordData("skin specialist in bhopal", "City Head Term", 4400, 0.08, 0.28, 17, "Tier 2 - Strong"),
        "dentist": KeywordData("dentist in bhopal", "City Head Term", 2400, 0.09, 0.23, 14, "Tier 2 - Strong"),
        "dental_clinic": KeywordData("dental clinic in bhopal", "City Head Term", 1600, 0.10, 0.11, 19, "Tier 2 - Strong"),
        "gynecologist": KeywordData("gynecologist in bhopal", "City Head Term", 4400, 0.09, 0.06, 19, "Tier 2 - Strong"),
        "orthopedic": KeywordData("orthopedic doctor in bhopal", "City Head Term", 3600, 0.01, 0.09, 15, "Tier 2 - Strong"),
        "physiotherapist": KeywordData("physiotherapist in bhopal", "City Head Term", 2400, 0.24, 0.17, 28, "Tier 2 - Strong"),
        "hair_transplant": KeywordData("hair transplant in bhopal", "City Head Term", 590, 0.34, 0.32, 15, "Tier 3 - Viable"),
    },
}

# Aliases for city name variations
CITY_ALIASES = {
    "bengaluru": "bangalore",
    "new delhi": "delhi",
    "delhi ncr": "delhi",
    "noida": "delhi",
    "gurugram": "delhi",
    "gurgaon": "delhi",
    "navi mumbai": "mumbai",
    "thane": "mumbai",
}

# Profession to specialty mapping
PROFESSION_TO_SPECIALTY = {
    "DENTIST": ["dentist", "dental_clinic"],
    "DERMATOLOGIST": ["dermatologist", "skin_specialist"],
    "ORTHOPEDIC": ["orthopedic", "physiotherapist"],
    "ENT": ["orthopedic"],  # Closest proxy
    "OPHTHALMOLOGIST": ["dermatologist"],  # Closest proxy for now
    "GYNECOLOGIST": ["gynecologist"],
    "PEDIATRICIAN": ["dentist"],  # Use dentist as proxy
    "SURGEON": ["orthopedic"],
    "GENERAL_PHYSICIAN": ["dentist"],  # Use as proxy
    "OTHER": ["dentist"],
}


class KeywordIntelligence:
    """Provides real market intelligence for campaign creation and optimization.

    Usage:
        intel = KeywordIntelligence()

        # Get market data for a dentist in Indore
        data = intel.get_market_data("indore", "DENTIST")

        # Get recommended keywords for a campaign
        keywords = intel.get_recommended_keywords("indore", "DENTIST", "dental implants")

        # Get estimated CPC and budget for a city+specialty
        estimate = intel.get_budget_estimate("indore", "DENTIST", target_clicks_per_day=20)
    """

    def get_market_data(self, city: str, specialty: str) -> dict:
        """Get complete market data for a specialty in a city.

        Returns search volumes, CPCs, competition levels, and recommended
        budget based on real data.
        """
        city_key = self._normalize_city(city)
        city_data = CITY_HEAD_TERMS.get(city_key, {})

        if not city_data:
            return {
                "city": city,
                "specialty": specialty,
                "data_available": False,
                "message": f"No keyword data available for {city}. Using default estimates.",
            }

        profession_keys = PROFESSION_TO_SPECIALTY.get(specialty, ["dentist"])
        results = []

        for prof_key in profession_keys:
            kw_data = city_data.get(prof_key)
            if kw_data:
                # Convert CPC from USD to INR (approx ₹83 per USD)
                cpc_inr = round(kw_data.cpc_usd * 83, 1)
                results.append({
                    "profession": prof_key,
                    "keyword": kw_data.keyword,
                    "search_volume": kw_data.search_volume_monthly,
                    "cpc_usd": kw_data.cpc_usd,
                    "cpc_inr": cpc_inr,
                    "competition": kw_data.competition_score,
                    "difficulty": kw_data.keyword_difficulty,
                    "priority_tier": kw_data.priority_tier,
                })

        total_volume = sum(r["search_volume"] for r in results)
        avg_cpc_inr = (
            sum(r["cpc_inr"] * r["search_volume"] for r in results) / total_volume
            if total_volume > 0 else 0
        )

        # Budget recommendation based on real CPC data
        recommended_daily = round(avg_cpc_inr * 20)  # Target 20 clicks/day
        recommended_monthly = round(recommended_daily * 30.4)

        return {
            "city": city,
            "city_normalized": city_key,
            "specialty": specialty,
            "data_available": True,
            "keywords": results,
            "total_monthly_search_volume": total_volume,
            "avg_cpc_inr": round(avg_cpc_inr, 1),
            "avg_competition": round(
                sum(r["competition"] for r in results) / len(results), 2
            ) if results else 0,
            "recommended_daily_budget_inr": recommended_daily,
            "recommended_monthly_budget_inr": recommended_monthly,
            "market_size": (
                "large" if total_volume > 10000
                else "medium" if total_volume > 3000
                else "small"
            ),
        }

    def get_recommended_keywords(
        self, city: str, specialty: str, treatment: str | None = None
    ) -> list[dict]:
        """Get recommended keywords for a campaign.

        Returns keywords with search volume and CPC data,
        ready to be used in Google Ads campaign creation.
        """
        city_key = self._normalize_city(city)
        city_data = CITY_HEAD_TERMS.get(city_key, {})

        keywords = []

        # Add city head terms for the specialty
        profession_keys = PROFESSION_TO_SPECIALTY.get(specialty, ["dentist"])
        for prof_key in profession_keys:
            kw_data = city_data.get(prof_key)
            if kw_data:
                keywords.append({
                    "keyword": kw_data.keyword,
                    "match_type": "phrase",
                    "search_volume": kw_data.search_volume_monthly,
                    "cpc_inr": round(kw_data.cpc_usd * 83, 1),
                    "priority": kw_data.priority_tier,
                    "source": "city_head_term",
                })

        # Add treatment-specific keywords
        if treatment:
            treatment_lower = treatment.lower()
            keywords.extend([
                {
                    "keyword": f"{treatment_lower} in {city_key}",
                    "match_type": "phrase",
                    "search_volume": None,  # Estimated
                    "cpc_inr": None,
                    "priority": "Tier 2 - Strong",
                    "source": "treatment_specific",
                },
                {
                    "keyword": f"best {treatment_lower} near me",
                    "match_type": "phrase",
                    "search_volume": None,
                    "cpc_inr": None,
                    "priority": "Tier 2 - Strong",
                    "source": "treatment_specific",
                },
                {
                    "keyword": f"{treatment_lower} cost in {city_key}",
                    "match_type": "phrase",
                    "search_volume": None,
                    "cpc_inr": None,
                    "priority": "Tier 3 - Viable",
                    "source": "treatment_specific",
                },
            ])

        # Add "near me" variations
        for prof_key in profession_keys:
            prof_display = prof_key.replace("_", " ")
            keywords.append({
                "keyword": f"best {prof_display} near me",
                "match_type": "broad",
                "search_volume": None,
                "cpc_inr": None,
                "priority": "Tier 2 - Strong",
                "source": "near_me",
            })

        return keywords

    def get_budget_estimate(
        self, city: str, specialty: str, target_clicks_per_day: int = 20
    ) -> dict:
        """Estimate daily/monthly budget based on real CPC data.

        Much more accurate than guessing — uses actual CPC from the market.
        """
        market = self.get_market_data(city, specialty)
        if not market.get("data_available"):
            # Fall back to general estimate
            return {
                "city": city,
                "specialty": specialty,
                "estimated_daily_budget_inr": target_clicks_per_day * 30,
                "estimated_monthly_budget_inr": target_clicks_per_day * 30 * 30,
                "data_source": "estimate",
            }

        avg_cpc = market["avg_cpc_inr"]
        daily_budget = round(avg_cpc * target_clicks_per_day)
        monthly_budget = round(daily_budget * 30.4)

        return {
            "city": city,
            "specialty": specialty,
            "avg_cpc_inr": avg_cpc,
            "target_clicks_per_day": target_clicks_per_day,
            "estimated_daily_budget_inr": daily_budget,
            "estimated_monthly_budget_inr": monthly_budget,
            "total_market_volume": market["total_monthly_search_volume"],
            "market_size": market["market_size"],
            "data_source": "real_keyword_data",
            "note": (
                f"Based on real CPC data for {specialty} in {city}. "
                f"Market has {market['total_monthly_search_volume']:,} monthly searches. "
                f"Average CPC ₹{avg_cpc:.0f}."
            ),
        }

    def get_all_cities(self) -> list[str]:
        """Return all cities with keyword data."""
        return list(CITY_HEAD_TERMS.keys())

    def _normalize_city(self, city: str) -> str:
        """Normalize city name to match our data keys."""
        city_lower = city.lower().strip()
        return CITY_ALIASES.get(city_lower, city_lower)


# Singleton instance
keyword_intelligence = KeywordIntelligence()
