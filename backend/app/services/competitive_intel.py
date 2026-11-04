"""Competitive intelligence module for healthcare advertising.

Monitors competitor ads, analyzes their strategies, and provides
actionable insights for campaign optimization.

Uses the Meta Ad Library API (public, no auth needed for transparency data)
and Google Ads Transparency Center.
"""

import logging
from datetime import datetime
from urllib.parse import quote_plus

import httpx

from app.models.doctor import Doctor

logger = logging.getLogger(__name__)

META_AD_LIBRARY_URL = "https://graph.facebook.com/v21.0/ads_archive"


class CompetitiveIntelService:
    """Gathers competitive intelligence from public ad transparency sources."""

    async def search_competitor_ads(
        self,
        doctor: Doctor,
        search_terms: list[str] | None = None,
    ) -> dict:
        """Search for competitor ads in the doctor's specialty and location.

        Uses the Meta Ad Library API to find active healthcare ads.

        Args:
            doctor: The doctor whose competitors to research
            search_terms: Optional custom search terms; defaults to specialty-based
        """
        specialty = doctor.specialty.value.replace("_", " ").lower() if doctor.specialty else "doctor"
        city = doctor.city or ""

        if not search_terms:
            search_terms = [
                f"{specialty} {city}",
                f"dental clinic {city}" if specialty == "dentist" else f"{specialty} clinic {city}",
                f"best {specialty} {city}",
            ]

        all_results = []
        for term in search_terms:
            ads = await self._search_meta_ad_library(term, country="IN")
            all_results.extend(ads)

        # Deduplicate by ad ID
        seen = set()
        unique_ads = []
        for ad in all_results:
            ad_id = ad.get("id", "")
            if ad_id not in seen:
                seen.add(ad_id)
                unique_ads.append(ad)

        # Analyze the results
        analysis = self._analyze_competitor_ads(unique_ads, doctor)

        return {
            "search_terms": search_terms,
            "total_competitor_ads": len(unique_ads),
            "ads": unique_ads[:20],  # Top 20 most relevant
            "analysis": analysis,
            "searched_at": datetime.utcnow().isoformat(),
        }

    async def _search_meta_ad_library(
        self, query: str, country: str = "IN", limit: int = 25
    ) -> list[dict]:
        """Search the Meta Ad Library API for ads matching a query.

        The Ad Library API is publicly accessible for transparency.
        """
        params = {
            "search_terms": query,
            "ad_reached_countries": country,
            "ad_active_status": "ACTIVE",
            "limit": limit,
            "fields": "id,ad_creative_bodies,ad_creative_link_titles,ad_creative_link_descriptions,page_name,ad_delivery_start_time,estimated_audience_size",
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(META_AD_LIBRARY_URL, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("data", [])
                else:
                    logger.warning("Ad Library search returned %d for '%s'", resp.status_code, query)
                    return []
        except httpx.HTTPError as exc:
            logger.error("Ad Library search failed: %s", exc)
            return []

    def _analyze_competitor_ads(self, ads: list[dict], doctor: Doctor) -> dict:
        """Analyze competitor ads to extract actionable insights.

        Looks at:
        - How many competitors are advertising
        - Common messaging themes
        - Estimated audience sizes
        - Ad frequency/volume per competitor
        """
        if not ads:
            return {
                "competitors_found": 0,
                "insight": "No active competitor ads found. This is an opportunity — you could be the only advertiser in your area.",
                "recommendations": [
                    "Launch campaigns quickly to establish presence before competitors",
                    "Even a small budget can dominate when competition is low",
                ],
            }

        # Count ads per page (competitor)
        page_counts: dict[str, int] = {}
        for ad in ads:
            page = ad.get("page_name", "Unknown")
            page_counts[page] = page_counts.get(page, 0) + 1

        top_competitors = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Analyze messaging
        all_bodies = []
        for ad in ads:
            bodies = ad.get("ad_creative_bodies", [])
            all_bodies.extend(bodies)

        # Common themes detection
        themes = []
        theme_keywords = {
            "price/offer": ["free", "discount", "offer", "₹", "affordable", "cheap", "cost"],
            "trust": ["years", "experience", "expert", "trusted", "certified", "award"],
            "urgency": ["today", "now", "limited", "book now", "hurry", "last"],
            "technology": ["laser", "digital", "painless", "advanced", "modern", "latest"],
            "location": ["near", "location", "visit", "walk-in", "convenient"],
        }

        body_text = " ".join(all_bodies).lower()
        for theme, keywords in theme_keywords.items():
            if any(kw in body_text for kw in keywords):
                themes.append(theme)

        total_ads = len(ads)
        num_competitors = len(page_counts)

        # Generate recommendations
        recommendations = []
        if num_competitors > 5:
            recommendations.append(
                f"High competition ({num_competitors} advertisers). "
                "Focus on specific treatments rather than general specialty keywords."
            )
        if "price/offer" in themes:
            recommendations.append(
                "Competitors are using price-based messaging. "
                "Differentiate with trust signals (experience, reviews, credentials)."
            )
        if "urgency" not in themes:
            recommendations.append(
                "Few competitors use urgency. Add 'Same-day appointments' or "
                "'Book today' CTAs to stand out."
            )
        if top_competitors and top_competitors[0][1] > 10:
            recommendations.append(
                f"'{top_competitors[0][0]}' is running {top_competitors[0][1]} ads — "
                "a serious competitor. Monitor their messaging and differentiate."
            )

        return {
            "competitors_found": num_competitors,
            "total_active_ads": total_ads,
            "top_competitors": [
                {"name": name, "active_ads": count}
                for name, count in top_competitors
            ],
            "messaging_themes": themes,
            "recommendations": recommendations,
            "market_intensity": (
                "high" if total_ads > 50
                else "medium" if total_ads > 15
                else "low"
            ),
        }

    async def get_google_ads_transparency(self, query: str, region: str = "IN") -> dict:
        """Get competitor data from Google Ads Transparency Center.

        NOTE: Google Ads Transparency Center doesn't have a public API,
        so this returns a link to the transparency page for manual review.
        """
        encoded = quote_plus(query)
        return {
            "url": f"https://adstransparency.google.com/advertiser?region={region}&q={encoded}",
            "note": "Visit the Google Ads Transparency Center to see competitor ads manually.",
        }

    async def generate_competitive_report(self, doctor: Doctor) -> dict:
        """Generate a full competitive intelligence report for a doctor."""
        meta_data = await self.search_competitor_ads(doctor)

        specialty = doctor.specialty.value.replace("_", " ").title() if doctor.specialty else "Healthcare"
        google_transparency = await self.get_google_ads_transparency(
            f"{specialty} {doctor.city}"
        )

        return {
            "doctor": doctor.full_name,
            "specialty": specialty,
            "city": doctor.city,
            "meta_ads": meta_data,
            "google_transparency": google_transparency,
            "generated_at": datetime.utcnow().isoformat(),
        }
