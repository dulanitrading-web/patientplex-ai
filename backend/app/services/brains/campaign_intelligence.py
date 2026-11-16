"""
Campaign Intelligence Engine — The smartest brain in PatientPlex.

This is the decision-making layer that sits ABOVE individual platform brains.
It analyzes REAL performance data and makes decisions like a senior performance
marketer who has managed ₹10Cr+ in healthcare ad spend.

KEY INTELLIGENCE:
1. NETWORK SELECTION: When to use Search vs Display vs Search Partners vs YouTube
2. CAMPAIGN TYPE: Which campaigns to create, pause, or scale
3. BID STRATEGY: Dynamic bid strategy selection based on data maturity
4. KEYWORD INTELLIGENCE: Which keywords are printing money vs burning cash
5. AUDIENCE INTELLIGENCE: Which demographics convert best
6. BUDGET REALLOCATION: Move money from losers to winners in real-time
7. CREATIVE INTELLIGENCE: Which ad copy patterns are winning
8. PLATFORM ARBITRAGE: Google vs Meta — where is the CPA cheaper right now?

PHILOSOPHY:
- Never make decisions without data. If no data → use industry benchmarks.
- Every ₹1 spent should be accountable.
- Optimize for appointments (conversions), not vanity metrics (clicks/impressions).
- Be aggressive with winners, ruthless with losers.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# NETWORK INTELLIGENCE — When to use which Google network
# ═══════════════════════════════════════════════════════════════

NETWORK_DECISION_MATRIX = {
    "google_search": {
        "when_to_use": "ALWAYS — this is your bread and butter",
        "best_for": [
            "High-intent keywords (dental implant cost indore)",
            "Near me searches (dentist near me)",
            "Emergency searches (tooth pain dentist now)",
            "Cost/price searches (braces cost indore)",
        ],
        "avg_ctr": 5.0,
        "avg_conversion_rate": 4.5,
        "avg_cpc_inr": 35,
        "priority": 1,
        "budget_share_min": 0.50,
        "budget_share_max": 0.80,
    },
    "search_partners": {
        "when_to_use": "Enable ONLY when Search campaigns have >3% CTR and profitable CPA",
        "best_for": [
            "Extending reach beyond Google.com",
            "Catching patients on Ask.com, AOL, partner sites",
            "Lower CPC than Google Search (usually 20-30% cheaper)",
        ],
        "risks": [
            "Lower quality traffic — lower conversion rate",
            "Less control over where ads appear",
            "Can dilute campaign metrics",
        ],
        "avg_ctr": 2.5,
        "avg_conversion_rate": 2.0,
        "avg_cpc_inr": 25,
        "priority": 3,
        "enable_rule": {
            "min_search_ctr": 3.0,
            "min_search_conversions_30d": 10,
            "cpa_headroom_pct": 20,  # Enable only if CPA is 20%+ below target
        },
        "budget_share_min": 0.0,
        "budget_share_max": 0.15,
    },
    "display_network": {
        "when_to_use": "Only for retargeting and brand awareness at scale",
        "best_for": [
            "Retargeting website visitors who didn't book (CRITICAL)",
            "Custom intent audiences — people who searched dental terms on Google",
            "In-market audiences — Google knows who's shopping for dental treatment",
            "Competitor targeting — show ads on competitor review pages",
        ],
        "NEVER_use_for": [
            "Cold prospecting on small budgets (<₹30K/month)",
            "Direct response campaigns without retargeting pixels",
            "Clinics without a landing page (nowhere to retarget from)",
        ],
        "campaign_types": {
            "retargeting": {
                "priority": "HIGH — cheapest conversions after search",
                "audience": "Website visitors 1-30 days, didn't convert",
                "avg_cpc_inr": 8,
                "avg_conversion_rate": 3.5,
                "budget_share": 0.10,
                "creative": "Show the treatment they viewed + limited offer",
            },
            "custom_intent": {
                "priority": "MEDIUM — good for awareness + consideration",
                "audience": "People who searched dental keywords recently",
                "avg_cpc_inr": 5,
                "avg_conversion_rate": 0.8,
                "budget_share": 0.05,
                "creative": "Before/after, doctor credibility, patient testimonials",
            },
            "in_market": {
                "priority": "MEDIUM — Google's AI identifies active shoppers",
                "audience": "People Google flagged as shopping for dental services",
                "avg_cpc_inr": 10,
                "avg_conversion_rate": 1.2,
                "budget_share": 0.05,
                "creative": "Strong offer + trust signals + easy booking CTA",
            },
            "competitor_placement": {
                "priority": "LOW — use sparingly",
                "audience": "Show on competitor websites, Practo, Justdial",
                "avg_cpc_inr": 3,
                "avg_conversion_rate": 0.5,
                "budget_share": 0.03,
                "creative": "Why we're different — comparison messaging",
            },
        },
        "avg_ctr": 0.5,
        "avg_conversion_rate": 1.0,
        "avg_cpc_inr": 8,
        "priority": 2,
        "budget_share_min": 0.05,
        "budget_share_max": 0.25,
    },
    "youtube": {
        "when_to_use": "Only for clinics with video content and budget >₹50K/month",
        "best_for": [
            "Before/after transformation videos (implants, smile design)",
            "Doctor credibility — 'meet your dentist' videos",
            "Treatment explainer videos (builds trust before booking)",
            "Retargeting website visitors with video testimonials",
        ],
        "requirements": [
            "Must have video content (even phone-shot is fine)",
            "Monthly budget >₹50K (YouTube needs volume)",
            "Landing page with video + booking form",
        ],
        "avg_cpv_inr": 1.5,
        "avg_view_rate": 30,
        "avg_conversion_rate": 0.3,
        "priority": 4,
        "budget_share_min": 0.0,
        "budget_share_max": 0.15,
    },
    "pmax": {
        "when_to_use": "Performance Max — when you have conversion data + all assets",
        "best_for": [
            "Clinics with 30+ conversions/month (Google needs data to optimize)",
            "Cross-network optimization — Google decides Search vs Display vs YouTube",
            "Scaling beyond manual campaign structure limits",
        ],
        "NEVER_use_for": [
            "New accounts with <15 conversions",
            "Clinics without proper conversion tracking",
            "When you need full keyword/placement control",
        ],
        "requirements": {
            "min_conversions_30d": 30,
            "assets_needed": ["headlines", "descriptions", "images", "logo", "video_optional"],
            "conversion_tracking": "MUST have phone call + form submit tracking",
        },
        "avg_conversion_rate": 5.0,
        "priority": 5,
        "budget_share_min": 0.0,
        "budget_share_max": 0.40,
    },
}


# ═══════════════════════════════════════════════════════════════
# META CAMPAIGN INTELLIGENCE — Which campaign types to run
# ═══════════════════════════════════════════════════════════════

META_CAMPAIGN_INTELLIGENCE = {
    "lead_gen_instant_form": {
        "when_to_use": "Best for quick lead capture — patient fills form without leaving Facebook",
        "best_for": ["Free consultation offers", "Discount offers", "Treatment inquiries"],
        "avg_cpl_inr": 150,
        "avg_lead_quality": "medium",  # Many fake/low-intent leads
        "conversion_rate_to_appointment": 0.15,  # 15% of leads book
        "optimization": "LEAD_GENERATION",
        "budget_priority": 2,
        "pro_tip": "Use higher-intent form (more questions) to filter serious patients",
    },
    "click_to_whatsapp": {
        "when_to_use": "BEST for Indian clinics — patients prefer WhatsApp over forms",
        "best_for": ["All clinics with WhatsApp Business", "Instant 2-way conversation"],
        "avg_cpl_inr": 80,
        "avg_lead_quality": "high",  # Patient actively started conversation
        "conversion_rate_to_appointment": 0.35,  # 35% of WA conversations book
        "optimization": "MESSAGES",
        "budget_priority": 1,
        "pro_tip": "Set up AI auto-responder to handle first message immediately",
    },
    "traffic_to_landing_page": {
        "when_to_use": "When clinic has a high-converting landing page (>5% conversion)",
        "best_for": ["SEO-optimized pages", "Pages with booking form + phone click"],
        "avg_cpc_inr": 12,
        "avg_landing_page_conv_rate": 0.04,
        "effective_cpl_inr": 300,
        "optimization": "LANDING_PAGE_VIEWS",
        "budget_priority": 3,
        "pro_tip": "Only use if landing page has phone tracking + form tracking",
    },
    "video_views_awareness": {
        "when_to_use": "Only for brand building — budget >₹50K/month on Meta alone",
        "best_for": [
            "New clinics building awareness in an area",
            "Doctor authority building (expert talking head)",
            "Before/after transformations (highest engagement)",
        ],
        "avg_cpv_inr": 0.5,
        "avg_reach_per_1000_inr": 80,
        "budget_priority": 4,
        "pro_tip": "Retarget video viewers (watched 50%+) with lead gen campaign",
    },
    "retargeting": {
        "when_to_use": "ALWAYS — cheapest conversions on Meta",
        "audiences": {
            "website_visitors_7d": {"priority": 1, "size_min": 100},
            "website_visitors_30d": {"priority": 2, "size_min": 500},
            "video_viewers_50pct": {"priority": 3, "size_min": 200},
            "ig_engagers_30d": {"priority": 4, "size_min": 300},
            "fb_page_engagers_30d": {"priority": 5, "size_min": 300},
        },
        "avg_cpl_inr": 50,
        "conversion_rate_to_appointment": 0.40,
        "budget_priority": 0,  # Highest priority — always fund this first
        "pro_tip": "Use urgency messaging: 'Still looking for a dentist? Limited slots this week'",
    },
}


# ═══════════════════════════════════════════════════════════════
# BIDDING STRATEGY INTELLIGENCE — Dynamic decision engine
# ═══════════════════════════════════════════════════════════════

BIDDING_INTELLIGENCE = {
    "google": {
        "manual_cpc": {
            "use_when": "New account OR need full control OR budget <₹10K/month",
            "data_needed": "None — works from day 1",
            "pros": "Full control over every keyword bid",
            "cons": "Time-intensive, misses patterns a machine would catch",
            "signals": {
                "conversions_30d": {"max": 5},
                "monthly_budget_inr": {"max": 10000},
            },
        },
        "maximize_clicks": {
            "use_when": "Data collection phase — need click volume to learn",
            "data_needed": "0-50 clicks",
            "pros": "Gets you traffic fast to learn which keywords convert",
            "cons": "Doesn't optimize for conversions — just clicks",
            "signals": {
                "conversions_30d": {"max": 10},
                "clicks_30d": {"max": 100},
            },
            "tip": "Set a max CPC cap = 2x your city's average CPC to avoid waste",
        },
        "maximize_conversions": {
            "use_when": "Enough conversion data for Google's ML to work",
            "data_needed": "15+ conversions in 30 days",
            "pros": "Google optimizes for what actually matters — appointments",
            "cons": "Can spend more aggressively if budget allows",
            "signals": {
                "conversions_30d": {"min": 15},
            },
            "tip": "Don't set a target CPA yet — let Google learn first for 2 weeks",
        },
        "target_cpa": {
            "use_when": "Mature account with stable CPA — most efficient strategy",
            "data_needed": "30+ conversions in 30 days + stable CPA for 2 weeks",
            "pros": "Precise cost control — you set the max per appointment",
            "cons": "Too aggressive target = no impressions. Too loose = waste",
            "signals": {
                "conversions_30d": {"min": 30},
                "cpa_stability_weeks": {"min": 2},
            },
            "tip": "Set target CPA = 120% of your current average CPA to start. Tighten by 10% weekly.",
        },
        "target_roas": {
            "use_when": "When different treatments have different values (implant vs cleaning)",
            "data_needed": "50+ conversions + conversion value tracking",
            "pros": "Optimizes for revenue, not just volume",
            "cons": "Needs conversion value tracking properly set up",
            "signals": {
                "conversions_30d": {"min": 50},
                "has_conversion_values": True,
            },
        },
    },
    "meta": {
        "lowest_cost": {
            "use_when": "Default — let Meta find the cheapest conversions",
            "data_needed": "None",
            "pros": "Simple, works well for most clinics",
            "cons": "No CPA control — Meta decides what to pay",
        },
        "cost_cap": {
            "use_when": "When you know your max CPA and have enough data",
            "data_needed": "50+ conversions in 30 days",
            "pros": "Won't exceed your CPA target",
            "cons": "Can limit delivery if cap is too tight",
            "tip": "Set cost cap = 130% of your average CPA",
        },
        "bid_cap": {
            "use_when": "Maximum control over auction bids",
            "data_needed": "Deep understanding of auction dynamics",
            "pros": "Prevents overpaying in any single auction",
            "cons": "Requires constant monitoring",
        },
    },
}


class CampaignIntelligence:
    """The smartest brain in PatientPlex — makes data-driven campaign decisions.

    This engine analyzes real performance data and outputs actionable decisions:
    - Which networks/campaigns to enable or disable
    - How to reallocate budget across campaigns
    - Which keywords to scale up or pause
    - When to change bidding strategy
    - What the next optimization move should be
    """

    def analyze_and_decide(self, campaigns: list[dict], monthly_budget: float, specialty: str = "DENTIST") -> dict:
        """The master decision function. Feed it campaign data, get back a complete strategy.

        campaigns: list of campaign dicts with metrics (from Google Ads API)
        monthly_budget: total monthly budget in INR
        specialty: doctor's specialty
        """
        total_spend = sum(c.get("spend_inr", 0) for c in campaigns)
        total_clicks = sum(c.get("clicks", 0) for c in campaigns)
        total_conversions = sum(c.get("conversions", 0) for c in campaigns)
        total_impressions = sum(c.get("impressions", 0) for c in campaigns)

        avg_cpa = round(total_spend / total_conversions, 2) if total_conversions > 0 else None
        avg_cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else None
        avg_ctr = round(total_clicks / total_impressions * 100, 2) if total_impressions > 0 else 0

        decisions = {
            "account_health": self._assess_account_health(campaigns, total_spend, total_conversions, avg_cpa, avg_ctr),
            "network_decisions": self._decide_networks(campaigns, monthly_budget, total_conversions),
            "bidding_decisions": self._decide_bidding(campaigns, total_conversions, avg_cpa),
            "budget_reallocation": self._reallocate_budget(campaigns, monthly_budget),
            "keyword_actions": self._keyword_intelligence(campaigns),
            "campaign_actions": self._campaign_actions(campaigns, monthly_budget),
            "meta_decisions": self._decide_meta_strategy(monthly_budget, total_conversions),
            "next_actions": [],
            "summary_metrics": {
                "total_spend_inr": total_spend,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "avg_cpa_inr": avg_cpa,
                "avg_cpc_inr": avg_cpc,
                "avg_ctr_pct": avg_ctr,
            },
        }

        # Generate prioritized action list
        decisions["next_actions"] = self._prioritize_actions(decisions)

        return decisions

    def _assess_account_health(self, campaigns, total_spend, total_conversions, avg_cpa, avg_ctr) -> dict:
        """Score the account 0-100 and identify the biggest problems."""
        score = 50  # Start at neutral
        issues = []
        wins = []

        # Conversion tracking
        if total_spend > 10000 and total_conversions == 0:
            score -= 30
            issues.append({
                "severity": "CRITICAL",
                "issue": "Spending money with ZERO conversions tracked",
                "action": "Set up conversion tracking immediately — phone calls + form submissions",
                "impact": "Without this, every rupee is unaccountable",
            })
        elif total_conversions > 0:
            score += 10
            wins.append("Conversion tracking is working")

        # CPA health
        if avg_cpa and avg_cpa > 5000:
            score -= 15
            issues.append({
                "severity": "HIGH",
                "issue": f"CPA is ₹{avg_cpa:,.0f} — too high for most treatments",
                "action": "Pause lowest-converting campaigns, add negative keywords, tighten targeting",
            })
        elif avg_cpa and avg_cpa < 1500:
            score += 15
            wins.append(f"CPA at ₹{avg_cpa:,.0f} is excellent")

        # CTR health
        if avg_ctr < 2.0 and len(campaigns) > 0:
            score -= 10
            issues.append({
                "severity": "MEDIUM",
                "issue": f"CTR at {avg_ctr}% is below healthcare benchmark (3-5%)",
                "action": "Improve ad copy — add prices, urgency, and city name in headlines",
            })
        elif avg_ctr > 4.0:
            score += 10
            wins.append(f"CTR at {avg_ctr}% is above average")

        # Campaign structure
        search_campaigns = [c for c in campaigns if c.get("campaign_type") == "SEARCH"]
        display_campaigns = [c for c in campaigns if c.get("campaign_type") == "DISPLAY"]

        if not search_campaigns:
            score -= 20
            issues.append({
                "severity": "CRITICAL",
                "issue": "No Search campaigns — missing highest-intent patients",
                "action": "Create Search campaigns for top 3 treatments immediately",
            })

        return {
            "score": max(0, min(100, score)),
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F",
            "issues": issues,
            "wins": wins,
        }

    def _decide_networks(self, campaigns, monthly_budget, total_conversions) -> dict:
        """Decide which Google networks to enable based on data and budget."""
        decisions = {}

        # SEARCH — Always enabled
        decisions["google_search"] = {
            "enabled": True,
            "reason": "Search captures highest-intent patients — always run this",
            "budget_share": 0.60,
        }

        # SEARCH PARTNERS — Enable only if Search is profitable
        search_ctr = 0
        search_conv = 0
        for c in campaigns:
            if c.get("campaign_type") == "SEARCH":
                if c.get("impressions", 0) > 0:
                    search_ctr = max(search_ctr, c.get("ctr", 0))
                search_conv += c.get("conversions", 0)

        enable_partners = search_ctr > 3.0 and search_conv >= 10
        decisions["search_partners"] = {
            "enabled": enable_partners,
            "reason": (
                f"Search CTR={search_ctr:.1f}%, Conversions={search_conv}. "
                + ("Profitable enough to extend to partners." if enable_partners
                   else "Not enough data yet — keep search partners OFF to preserve budget quality.")
            ),
            "budget_share": 0.10 if enable_partners else 0.0,
        }

        # DISPLAY — Only for retargeting or large budgets
        has_retargeting_pixel = any(c.get("campaign_type") == "DISPLAY" for c in campaigns)
        large_budget = monthly_budget >= 30000

        enable_display = has_retargeting_pixel or (large_budget and total_conversions >= 15)
        decisions["display_network"] = {
            "enabled": enable_display,
            "campaign_types_to_run": [],
            "reason": "",
            "budget_share": 0.0,
        }

        if enable_display:
            display_types = []
            budget_share = 0.0

            # Retargeting — ALWAYS if we have pixel data
            display_types.append({
                "type": "retargeting",
                "priority": "CRITICAL",
                "audience": "Website visitors 1-30 days who didn't book",
                "expected_cpa_inr": 500,
                "budget_share": 0.08,
            })
            budget_share += 0.08

            # Custom intent — if budget allows
            if monthly_budget >= 50000:
                display_types.append({
                    "type": "custom_intent",
                    "priority": "MEDIUM",
                    "audience": "People who searched dental keywords on Google recently",
                    "expected_cpa_inr": 1500,
                    "budget_share": 0.05,
                })
                budget_share += 0.05

            # In-market — if enough conversions
            if total_conversions >= 30 and monthly_budget >= 75000:
                display_types.append({
                    "type": "in_market",
                    "priority": "MEDIUM",
                    "audience": "Google-identified dental service shoppers",
                    "expected_cpa_inr": 2000,
                    "budget_share": 0.05,
                })
                budget_share += 0.05

            decisions["display_network"]["campaign_types_to_run"] = display_types
            decisions["display_network"]["budget_share"] = budget_share
            decisions["display_network"]["reason"] = f"Display enabled with {len(display_types)} campaign types"
        else:
            decisions["display_network"]["reason"] = (
                "Display OFF — " +
                ("Budget too small for effective display" if not large_budget
                 else "Not enough conversion data to optimize display targeting")
            )

        # YOUTUBE — Only with video content and large budget
        enable_youtube = monthly_budget >= 50000 and total_conversions >= 20
        decisions["youtube"] = {
            "enabled": enable_youtube,
            "reason": (
                "YouTube enabled — budget and conversion data support video campaigns"
                if enable_youtube else
                "YouTube OFF — need ₹50K+ budget and 20+ conversions first"
            ),
            "budget_share": 0.08 if enable_youtube else 0.0,
        }

        # PMAX — Only mature accounts
        enable_pmax = total_conversions >= 30
        decisions["performance_max"] = {
            "enabled": enable_pmax,
            "reason": (
                f"PMax enabled — {total_conversions} conversions gives Google enough data to optimize across all networks"
                if enable_pmax else
                f"PMax OFF — need 30+ conversions (currently {total_conversions}). Stick with manual campaign structure."
            ),
            "budget_share": 0.25 if enable_pmax else 0.0,
        }

        return decisions

    def _decide_bidding(self, campaigns, total_conversions, avg_cpa) -> dict:
        """Decide the optimal bidding strategy for each campaign."""
        recommendations = []

        for c in campaigns:
            conv = c.get("conversions", 0)
            clicks = c.get("clicks", 0)
            spend = c.get("spend_inr", 0)
            campaign_cpa = round(spend / conv, 2) if conv > 0 else None

            if conv >= 30:
                strategy = "TARGET_CPA"
                target = round(campaign_cpa * 1.1) if campaign_cpa else 2000
                reason = f"{conv} conversions — enough for Target CPA. Set at ₹{target} (10% above current avg)"
            elif conv >= 15:
                strategy = "MAXIMIZE_CONVERSIONS"
                target = None
                reason = f"{conv} conversions — use Maximize Conversions, no target CPA yet"
            elif clicks >= 50:
                strategy = "MAXIMIZE_CLICKS"
                target = None
                reason = f"{clicks} clicks but only {conv} conversions — still learning, use Max Clicks with cap"
            else:
                strategy = "MANUAL_CPC"
                target = None
                reason = f"Only {clicks} clicks — use Manual CPC for full control during ramp-up"

            recommendations.append({
                "campaign_name": c.get("name", "Unknown"),
                "current_strategy": c.get("bid_strategy", "unknown"),
                "recommended_strategy": strategy,
                "target_cpa_inr": target,
                "reason": reason,
                "change_needed": c.get("bid_strategy", "").upper() != strategy,
            })

        return {"campaigns": recommendations}

    def _reallocate_budget(self, campaigns, monthly_budget) -> dict:
        """Reallocate budget from underperformers to winners."""
        if not campaigns:
            return {"reallocation": [], "reason": "No campaigns to reallocate"}

        daily_budget = round(monthly_budget / 30.4)

        # Score each campaign
        scored = []
        for c in campaigns:
            conv = c.get("conversions", 0)
            spend = c.get("spend_inr", 0)
            clicks = c.get("clicks", 0)
            impressions = c.get("impressions", 0)

            # Performance score (0-100)
            score = 0
            if conv > 0:
                cpa = spend / conv
                if cpa < 1000: score += 40
                elif cpa < 2000: score += 30
                elif cpa < 3000: score += 20
                elif cpa < 5000: score += 10
            if clicks > 0 and impressions > 0:
                ctr = clicks / impressions * 100
                if ctr > 5: score += 30
                elif ctr > 3: score += 20
                elif ctr > 2: score += 10
            if conv > 0:
                score += min(conv * 3, 30)  # More conversions = higher score

            scored.append({**c, "_score": score})

        # Sort by score descending
        scored.sort(key=lambda x: x["_score"], reverse=True)
        total_score = sum(c["_score"] for c in scored) or 1

        reallocation = []
        for c in scored:
            share = c["_score"] / total_score
            new_daily = max(round(daily_budget * share), 100)
            old_daily = c.get("daily_budget_inr", 0)

            action = "increase" if new_daily > old_daily * 1.15 else "decrease" if new_daily < old_daily * 0.85 else "keep"

            reallocation.append({
                "campaign_name": c.get("name", "Unknown"),
                "performance_score": c["_score"],
                "current_daily_inr": old_daily,
                "recommended_daily_inr": new_daily,
                "action": action,
                "reason": f"Score {c['_score']}/100 — {'top performer, scale up' if action == 'increase' else 'underperformer, reduce' if action == 'decrease' else 'performing as expected'}",
            })

        return {"reallocation": reallocation, "daily_budget_total": daily_budget}

    def _keyword_intelligence(self, campaigns) -> dict:
        """Analyze keyword-level data and recommend actions."""
        actions = {
            "scale_up": [],   # High-performing keywords → increase bids
            "pause": [],      # Wasting money → pause immediately
            "add_negative": [],  # Bad search terms → block
            "test_new": [],   # Opportunity keywords to test
        }

        for c in campaigns:
            keywords = c.get("keyword_data", [])
            for kw in keywords:
                spend = kw.get("cost_inr", 0)
                clicks = kw.get("clicks", 0)
                conv = kw.get("conversions", 0)
                impressions = kw.get("impressions", 0)

                if conv > 0 and spend > 0:
                    kw_cpa = spend / conv
                    if kw_cpa < 1500:
                        actions["scale_up"].append({
                            "keyword": kw.get("keyword", ""),
                            "cpa_inr": round(kw_cpa),
                            "conversions": conv,
                            "action": "INCREASE BID 20% — printing money",
                        })
                elif spend > 1000 and conv == 0:
                    actions["pause"].append({
                        "keyword": kw.get("keyword", ""),
                        "spend_wasted_inr": round(spend),
                        "clicks": clicks,
                        "action": f"PAUSE — spent ₹{spend:.0f} with 0 conversions",
                    })
                elif clicks == 0 and impressions > 200:
                    actions["add_negative"].append({
                        "keyword": kw.get("keyword", ""),
                        "impressions": impressions,
                        "action": "Consider pausing — high impressions but 0 clicks (low relevance)",
                    })

        return actions

    def _campaign_actions(self, campaigns, monthly_budget) -> list:
        """Decide which campaigns to create, pause, or scale."""
        actions = []

        campaign_types = [c.get("campaign_type", "") for c in campaigns]
        has_search = "SEARCH" in campaign_types
        has_display = "DISPLAY" in campaign_types
        has_call_only = "CALL_ONLY" in campaign_types

        # Missing campaign types
        if not has_search:
            actions.append({
                "action": "CREATE",
                "campaign_type": "SEARCH",
                "priority": "CRITICAL",
                "reason": "No Search campaigns — you're missing patients actively looking for treatment",
            })

        if not has_call_only and monthly_budget >= 15000:
            actions.append({
                "action": "CREATE",
                "campaign_type": "CALL_ONLY",
                "priority": "HIGH",
                "reason": "No Call-Only campaign — 40% of dental patients prefer calling over forms",
            })

        if not has_display and monthly_budget >= 30000:
            actions.append({
                "action": "CREATE",
                "campaign_type": "DISPLAY_RETARGETING",
                "priority": "HIGH",
                "reason": "No retargeting — website visitors are leaving without booking. Cheapest conversions.",
            })

        # Pause underperformers
        for c in campaigns:
            spend = c.get("spend_inr", 0)
            conv = c.get("conversions", 0)
            clicks = c.get("clicks", 0)

            if spend > 5000 and conv == 0 and clicks > 50:
                actions.append({
                    "action": "PAUSE",
                    "campaign_name": c.get("name", ""),
                    "priority": "HIGH",
                    "reason": f"Spent ₹{spend:,.0f} with 0 conversions — bleeding money",
                })

        return actions

    def _decide_meta_strategy(self, monthly_budget, total_google_conversions) -> dict:
        """Decide the Meta Ads strategy based on overall account performance."""
        meta_budget = 0
        campaigns_to_run = []

        if monthly_budget < 10000:
            return {
                "enabled": False,
                "reason": "Budget <₹10K — put everything on Google Search first",
                "meta_budget_inr": 0,
            }

        # Budget allocation to Meta
        if monthly_budget < 30000:
            meta_budget = round(monthly_budget * 0.20)
        elif monthly_budget < 75000:
            meta_budget = round(monthly_budget * 0.35)
        else:
            meta_budget = round(monthly_budget * 0.45)

        # Always run retargeting if pixel is active
        campaigns_to_run.append({
            "type": "retargeting",
            "budget_share": 0.20,
            "priority": 1,
            "reason": "Cheapest conversions — re-engage website visitors",
        })

        # Click-to-WhatsApp — best for India
        campaigns_to_run.append({
            "type": "click_to_whatsapp",
            "budget_share": 0.40,
            "priority": 1,
            "reason": "Highest conversion rate for Indian clinics — patients prefer WhatsApp",
        })

        # Lead gen — if budget allows
        if meta_budget >= 15000:
            campaigns_to_run.append({
                "type": "lead_gen_instant_form",
                "budget_share": 0.25,
                "priority": 2,
                "reason": "Capture leads directly on Facebook — use higher-intent form",
            })

        # Awareness — only large budgets
        if meta_budget >= 30000:
            campaigns_to_run.append({
                "type": "video_views_awareness",
                "budget_share": 0.15,
                "priority": 3,
                "reason": "Build brand awareness in the area with video content",
            })

        return {
            "enabled": True,
            "meta_budget_inr": meta_budget,
            "meta_daily_inr": round(meta_budget / 30.4),
            "campaigns_to_run": campaigns_to_run,
            "bidding_strategy": (
                "cost_cap" if total_google_conversions >= 50
                else "lowest_cost"
            ),
            "bidding_reason": (
                "Enough overall conversion data — use Cost Cap for CPA control"
                if total_google_conversions >= 50
                else "Not enough data — use Lowest Cost and let Meta's ML learn"
            ),
        }

    def _prioritize_actions(self, decisions: dict) -> list:
        """Create a ranked list of next actions from all decision outputs."""
        actions = []

        # From account health
        for issue in decisions["account_health"].get("issues", []):
            actions.append({
                "priority": 1 if issue["severity"] == "CRITICAL" else 2 if issue["severity"] == "HIGH" else 3,
                "action": issue["action"],
                "category": "account_health",
                "severity": issue["severity"],
            })

        # From campaign actions
        for ca in decisions.get("campaign_actions", []):
            prio_map = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3}
            actions.append({
                "priority": prio_map.get(ca.get("priority", "MEDIUM"), 3),
                "action": f"{ca['action']} {ca.get('campaign_type', ca.get('campaign_name', ''))} — {ca['reason']}",
                "category": "campaign_structure",
                "severity": ca.get("priority", "MEDIUM"),
            })

        # From bidding decisions
        for bd in decisions["bidding_decisions"].get("campaigns", []):
            if bd.get("change_needed"):
                actions.append({
                    "priority": 2,
                    "action": f"Change {bd['campaign_name']} bidding to {bd['recommended_strategy']} — {bd['reason']}",
                    "category": "bidding",
                    "severity": "HIGH",
                })

        # From budget reallocation
        for ra in decisions["budget_reallocation"].get("reallocation", []):
            if ra["action"] != "keep":
                actions.append({
                    "priority": 3,
                    "action": f"{'Increase' if ra['action'] == 'increase' else 'Decrease'} {ra['campaign_name']} budget to ₹{ra['recommended_daily_inr']}/day — {ra['reason']}",
                    "category": "budget",
                    "severity": "MEDIUM",
                })

        # Sort by priority
        actions.sort(key=lambda x: x["priority"])
        return actions[:15]  # Top 15 actions


# Singleton
campaign_intelligence = CampaignIntelligence()
