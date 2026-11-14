"""Website SEO service — on-page optimization, keyword tracking, and content generation.

Provides:
- On-page SEO audit for clinic websites
- Keyword research and tracking for medical specialties
- Meta tag and schema markup generation (MedicalBusiness, Physician)
- Local SEO optimization (Google My Business sync)
- AI-generated NMC-compliant blog content for organic traffic
- Competitor SEO analysis
- Monthly SEO report generation
"""

import logging
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)


class SEOService:
    """Manages website SEO for healthcare clinics."""

    # ─── On-Page SEO Audit ───

    async def audit_website(self, doctor, url: str = "") -> dict:
        """Run a comprehensive on-page SEO audit.

        Checks: title tags, meta descriptions, H1/H2 structure, image alt text,
        page speed indicators, mobile-friendliness, schema markup, internal linking.
        """
        clinic_url = url or f"https://{doctor.clinic_name.lower().replace(' ', '-')}.patientplex.ai"

        # Demo mode — return structured audit
        return {
            "demo_mode": True,
            "url": clinic_url,
            "score": 72,
            "max_score": 100,
            "checks": [
                {"name": "Title Tag", "status": "warning", "detail": "Title is 67 chars — keep under 60 for Google display", "priority": "high"},
                {"name": "Meta Description", "status": "pass", "detail": "155 characters, includes target keyword", "priority": "high"},
                {"name": "H1 Tag", "status": "pass", "detail": "Single H1 with primary keyword", "priority": "high"},
                {"name": "Schema Markup", "status": "fail", "detail": "No MedicalBusiness schema found — adding this improves local search", "priority": "high"},
                {"name": "Image Alt Text", "status": "warning", "detail": "3 of 8 images missing alt text", "priority": "medium"},
                {"name": "Page Speed", "status": "warning", "detail": "LCP 3.2s — target under 2.5s", "priority": "medium"},
                {"name": "Mobile Friendly", "status": "pass", "detail": "Responsive layout, touch targets OK", "priority": "high"},
                {"name": "Internal Links", "status": "warning", "detail": "Treatment pages have no cross-links", "priority": "low"},
                {"name": "SSL Certificate", "status": "pass", "detail": "HTTPS active, certificate valid", "priority": "high"},
                {"name": "Robots.txt", "status": "pass", "detail": "Properly configured", "priority": "medium"},
            ],
            "recommendations": [
                "Add MedicalBusiness and Physician schema markup for rich snippets in search",
                "Shorten title tag to under 60 characters",
                "Add alt text to 3 missing images with treatment-relevant keywords",
                "Optimize LCP — compress hero image and defer non-critical CSS",
                "Add internal links between related treatment pages",
            ],
            "message": "Connect your website URL for a live SEO audit",
        }

    # ─── Keyword Research ───

    async def get_keyword_suggestions(self, doctor, treatment: str = "") -> dict:
        """Get keyword suggestions for a clinic's specialty and treatments.

        Returns keywords with search volume, competition, and CPC estimates
        based on the clinic's specialty and location.
        """
        specialty = getattr(doctor, "specialty", "dental")
        city = getattr(doctor, "city", "Mumbai")

        keyword_data = {
            "dental": [
                {"keyword": f"dentist near me {city}", "volume": 12000, "competition": "medium", "cpc": 15},
                {"keyword": f"teeth whitening {city}", "volume": 4800, "competition": "high", "cpc": 25},
                {"keyword": f"dental implants cost {city}", "volume": 3200, "competition": "high", "cpc": 45},
                {"keyword": f"root canal treatment {city}", "volume": 2900, "competition": "medium", "cpc": 20},
                {"keyword": f"braces cost {city}", "volume": 2400, "competition": "medium", "cpc": 18},
                {"keyword": f"best dentist {city}", "volume": 6500, "competition": "high", "cpc": 30},
            ],
            "dermatology": [
                {"keyword": f"dermatologist near me {city}", "volume": 9500, "competition": "medium", "cpc": 20},
                {"keyword": f"skin specialist {city}", "volume": 7200, "competition": "medium", "cpc": 18},
                {"keyword": f"laser hair removal cost {city}", "volume": 5100, "competition": "high", "cpc": 35},
                {"keyword": f"acne treatment {city}", "volume": 4300, "competition": "medium", "cpc": 15},
                {"keyword": f"PRP treatment {city}", "volume": 2800, "competition": "high", "cpc": 40},
            ],
        }

        keywords = keyword_data.get(specialty, keyword_data["dental"])
        if treatment:
            keywords = [k for k in keywords if treatment.lower() in k["keyword"].lower()] or keywords

        return {
            "demo_mode": True,
            "specialty": specialty,
            "city": city,
            "keywords": keywords,
            "total_monthly_volume": sum(k["volume"] for k in keywords),
            "avg_cpc_inr": round(sum(k["cpc"] for k in keywords) / len(keywords), 1),
        }

    # ─── Schema Markup Generation ───

    async def generate_schema(self, doctor) -> dict:
        """Generate JSON-LD schema markup for the clinic website.

        Creates MedicalBusiness, Physician, and LocalBusiness schemas
        that improve Google rich snippet visibility.
        """
        clinic_name = getattr(doctor, "clinic_name", "My Clinic")
        city = getattr(doctor, "city", "Mumbai")
        specialty = getattr(doctor, "specialty", "Dentistry")

        schema = {
            "@context": "https://schema.org",
            "@type": "MedicalBusiness",
            "name": clinic_name,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": city,
                "addressCountry": "IN",
            },
            "medicalSpecialty": specialty,
            "telephone": getattr(doctor, "phone", ""),
            "openingHours": "Mo-Sa 09:00-20:00",
            "priceRange": "₹₹",
        }

        return {
            "schema_json": schema,
            "html_snippet": f'<script type="application/ld+json">{__import__("json").dumps(schema, indent=2)}</script>',
            "instructions": "Add this to the <head> of your website's homepage and treatment pages",
        }

    # ─── AI Blog Content ───

    async def generate_blog_outline(self, doctor, topic: str) -> dict:
        """Generate an NMC-compliant blog post outline for SEO.

        Creates keyword-optimized, medically accurate content outlines
        that drive organic traffic without violating NMC advertising rules.
        """
        return {
            "topic": topic,
            "suggested_title": f"{topic} — What You Need to Know | {getattr(doctor, 'clinic_name', 'My Clinic')}",
            "target_keyword": topic.lower(),
            "word_count": "1,200–1,500",
            "outline": [
                {"h2": f"What is {topic}?", "notes": "Define in simple terms, cite medical sources"},
                {"h2": "Who needs it?", "notes": "Symptoms and conditions, use 'People Also Ask' format"},
                {"h2": "How it works", "notes": "Step-by-step process, what to expect"},
                {"h2": "Benefits and risks", "notes": "Balanced view, NMC-compliant language"},
                {"h2": f"Cost of {topic} in {getattr(doctor, 'city', 'India')}", "notes": "Range, not guarantees; factors that affect pricing"},
                {"h2": "Frequently asked questions", "notes": "4–5 FAQs from Google 'People Also Ask'"},
                {"h2": "When to see a doctor", "notes": "Call to action — book a consultation"},
            ],
            "seo_tips": [
                "Use the target keyword in title, H1, first paragraph, and 2–3 H2s",
                "Add internal links to your treatment and booking pages",
                "Include 2–3 images with keyword-rich alt text",
                "Add FAQ schema markup for the FAQ section",
                "Keep language educational, not promotional (NMC compliance)",
            ],
        }

    # ─── Monthly SEO Report ───

    async def get_seo_report(self, doctor, days: int = 30) -> dict:
        """Generate a monthly SEO performance report.

        Tracks: organic traffic, keyword rankings, page performance,
        backlinks, and local SEO metrics.
        """
        return {
            "demo_mode": True,
            "period": f"Last {days} days",
            "organic_traffic": {
                "sessions": 847,
                "users": 612,
                "pageviews": 2340,
                "avg_session_duration": "2m 18s",
                "bounce_rate": "45.2%",
                "trend": "+12% vs previous period",
            },
            "top_pages": [
                {"page": "/", "views": 892, "avg_time": "1:45"},
                {"page": "/treatments/teeth-whitening", "views": 234, "avg_time": "3:12"},
                {"page": "/treatments/dental-implants", "views": 189, "avg_time": "2:56"},
                {"page": "/about", "views": 121, "avg_time": "1:20"},
                {"page": "/blog/cost-of-braces", "views": 98, "avg_time": "4:05"},
            ],
            "keyword_rankings": [
                {"keyword": "dentist near me", "position": 8, "change": "+3"},
                {"keyword": "teeth whitening cost", "position": 12, "change": "+5"},
                {"keyword": "dental clinic", "position": 15, "change": "+2"},
            ],
            "local_seo": {
                "gmb_views": 1240,
                "gmb_searches": 890,
                "gmb_actions": 156,
                "map_pack_appearances": 45,
            },
            "recommendations": [
                "Publish 2 blog posts targeting 'dental implants cost' and 'braces vs aligners'",
                "Add FAQ schema to top 3 treatment pages",
                "Get 5 new Google reviews this month to improve local pack ranking",
                "Fix 3 broken internal links found on treatment pages",
            ],
            "message": "Connect Google Search Console and GA4 for live SEO data",
        }


seo_service = SEOService()
