"""
PatientPlex Knowledge Library — Key frameworks, books, and mental models
that power the AI's decision-making.

This is the "education" of the AI — the strategic thinking layer above
the tactical benchmark data. These principles are referenced when the AI
makes campaign decisions, writes ad copy, advises clinics, or optimizes spend.
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# Books & Frameworks that inform the AI's strategy
# ---------------------------------------------------------------------------

KNOWLEDGE_LIBRARY = {

    # ===== MARKETING & GROWTH =====
    "scientific_advertising": {
        "title": "Scientific Advertising",
        "author": "Claude Hopkins (1923)",
        "category": "marketing_foundations",
        "key_principles": [
            "Every ad must make a proposition — what does the reader get?",
            "Headlines select the right readers — don't try to reach everyone",
            "Be specific: '₹3,000 root canal' beats 'affordable dental care'",
            "Test everything — never assume what works, measure it",
            "Samples and trials reduce risk — '14-day free trial' works because Hopkins proved it 100 years ago",
            "One story, one idea per ad — never crowd multiple propositions",
        ],
        "how_ai_uses_it": "When generating ad copy, the AI follows Hopkins' rule: ONE proposition per ad, SPECIFIC numbers, headline that SELECTS the right reader.",
    },
    "ogilvy_on_advertising": {
        "title": "Ogilvy on Advertising",
        "author": "David Ogilvy (1983)",
        "category": "marketing_foundations",
        "key_principles": [
            "The headline is 80% of the ad — if it doesn't work, you've wasted 80% of your money",
            "Promise a benefit in the headline — 'How to win friends and influence people'",
            "Long copy sells more than short copy (for considered purchases like IVF, implants)",
            "Use testimonials — they're the most powerful form of advertising (but NMC restricts this for healthcare in India)",
            "Don't be boring — nobody was ever bored into buying anything",
            "Research first, then create — know the patient before you write the ad",
        ],
        "how_ai_uses_it": "Headlines always lead with a benefit. For high-ATV treatments (IVF, implants), the AI generates longer WhatsApp sequences with more detail. For low-ATV (cleaning, consultation), it's short and direct.",
    },
    "breakthrough_advertising": {
        "title": "Breakthrough Advertising",
        "author": "Eugene Schwartz (1966)",
        "category": "marketing_foundations",
        "key_principles": [
            "5 stages of market awareness: Unaware → Problem-aware → Solution-aware → Product-aware → Most-aware",
            "Match your ad to the prospect's awareness stage",
            "Unaware: educate about the problem (Meta Reels — 'Did you know your toothache could be an infection?')",
            "Problem-aware: agitate the problem (Google Search — 'tooth pain treatment')",
            "Solution-aware: present your solution (Google Ads — 'Root canal at {clinic} starting ₹3,000')",
            "Product-aware: overcome objections (WhatsApp nurture — 'Here's what our patients say...')",
            "Most-aware: make the offer (WhatsApp — 'Book today, get 10% off consultation')",
            "You cannot create desire — you can only channel it",
        ],
        "how_ai_uses_it": [
            "Meta Reels = Unaware → Problem-aware (create demand)",
            "Google Ads = Problem/Solution-aware (capture demand)",
            "WhatsApp AI = Solution → Product-aware (nurture to booking)",
            "The AI selects the right message for each stage of the funnel",
        ],
    },
    "influence_cialdini": {
        "title": "Influence: The Psychology of Persuasion",
        "author": "Robert Cialdini (1984)",
        "category": "psychology",
        "key_principles": [
            "Reciprocity: Give value first (free consultation) → patient feels obligation to book",
            "Social proof: '500+ patients treated' — but NMC-compliant, no fake numbers",
            "Authority: 'Dr. {name}, {qualification}, {years} experience' — credentials build trust",
            "Scarcity: 'Only 3 slots left this week' — but MUST be real, never fake scarcity",
            "Consistency: Once someone asks a question on WhatsApp, they're more likely to book (foot-in-the-door)",
            "Liking: Doctor's face in ads builds connection — UGC outperforms stock photos 3x",
        ],
        "how_ai_uses_it": "WhatsApp nurture sequences use reciprocity (free info first), social proof (patient count), scarcity (limited slots — real calendar data), and consistency (micro-commitments).",
    },
    "hooked_nir_eyal": {
        "title": "Hooked: How to Build Habit-Forming Products",
        "author": "Nir Eyal (2014)",
        "category": "product",
        "key_principles": [
            "Hook model: Trigger → Action → Variable Reward → Investment",
            "External trigger: Google Ad or WhatsApp notification",
            "Internal trigger: Pain (toothache, hair loss, infertility anxiety)",
            "Action: Click ad, message on WhatsApp (must be EASY — one tap)",
            "Variable reward: AI responds instantly with relevant info (dopamine hit)",
            "Investment: Patient provides info (name, treatment, schedule) → increases switching cost",
        ],
        "how_ai_uses_it": "The AI receptionist is designed as a hook: instant response (variable reward), then asks for name/treatment (investment). Each interaction deepens commitment.",
    },

    # ===== BUSINESS STRATEGY =====
    "zero_to_one": {
        "title": "Zero to One",
        "author": "Peter Thiel (2014)",
        "category": "strategy",
        "key_principles": [
            "Monopoly is the condition of every successful business",
            "Start with a small market you can dominate — then expand",
            "What important truth do very few people agree with you on?",
            "PatientPlex's truth: Indian clinics don't need agencies — they need AI that works 24/7",
            "Build something 10x better, not 10% better — our AI receptionist is 10x faster than human",
            "Last mover advantage: be the LAST entrant in a market by being so good nobody can follow",
        ],
        "how_ai_uses_it": "The AI focuses on DOMINATING one specialty in one city before expanding. Don't try to be everything everywhere — be the best dental marketing tool in Hyderabad first.",
    },
    "lean_startup": {
        "title": "The Lean Startup",
        "author": "Eric Ries (2011)",
        "category": "strategy",
        "key_principles": [
            "Build-Measure-Learn loop — ship fast, measure, iterate",
            "Minimum Viable Product — what's the smallest thing that delivers value?",
            "Vanity metrics vs actionable metrics — clicks don't matter, booked patients do",
            "Pivot or persevere — if dental doesn't work, try dermatology",
            "Innovation accounting: track progress with learning milestones, not revenue (early stage)",
        ],
        "how_ai_uses_it": "The AI tracks actionable metrics only: CPL, cost-per-booking, cost-per-attending-patient, ROAS. It ignores vanity metrics like impressions and clicks when making optimization decisions.",
    },
    "crossing_the_chasm": {
        "title": "Crossing the Chasm",
        "author": "Geoffrey Moore (1991)",
        "category": "strategy",
        "key_principles": [
            "Technology adoption: Innovators → Early Adopters → Early Majority → Late Majority → Laggards",
            "The 'chasm' is between Early Adopters and Early Majority",
            "To cross: dominate a niche (beachhead), then expand",
            "Whole product concept: deliver everything the customer needs, not just the technology",
            "For PatientPlex: Tech-savvy cosmetic dermatologists (innovators) → All dermatologists (early adopters) → All dental (early majority) → All healthcare (late majority)",
        ],
        "how_ai_uses_it": "Sales targeting: the AI prioritizes clinics that show tech-savviness signals (website exists, Google reviews active, social media presence) — these are the innovators/early adopters.",
    },

    # ===== DATA & AI =====
    "thinking_fast_and_slow": {
        "title": "Thinking, Fast and Slow",
        "author": "Daniel Kahneman (2011)",
        "category": "psychology",
        "key_principles": [
            "System 1 (fast/intuitive) vs System 2 (slow/rational)",
            "Patients use System 1 for emergency decisions (tooth pain → nearest dentist)",
            "Patients use System 2 for elective decisions (IVF, hair transplant → research for weeks)",
            "Anchoring effect: show the expensive option first → cheaper option feels like a deal",
            "Loss aversion: 'You're losing ₹50K/month in missed patients' > 'You could gain ₹50K/month'",
            "Framing: '95% success rate' > '5% failure rate' — same data, different response",
        ],
        "how_ai_uses_it": "Ad copy for emergency (tooth pain, chest pain) uses System 1 triggers: urgency, proximity, availability. For elective (IVF, cosmetic), it uses System 2: detailed information, success rates, cost breakdowns, EMI options.",
    },
    "prediction_machines": {
        "title": "Prediction Machines: The Simple Economics of AI",
        "author": "Ajay Agrawal, Joshua Gans, Avi Goldfarb (2018)",
        "category": "ai_strategy",
        "key_principles": [
            "AI reduces the cost of prediction — prediction is the core task",
            "When prediction is cheap: use it everywhere (predict which lead will convert, predict best time to message, predict which keyword will perform)",
            "Data is the new oil — but only if you can turn it into predictions",
            "AI complements human judgment — AI predicts, human decides",
            "PatientPlex predictions: lead conversion probability, optimal bid amount, best send time, churn risk, treatment demand",
        ],
        "how_ai_uses_it": "Every data point collected feeds into prediction models. The AI predicts: which leads will convert (prioritize follow-up), when to send messages (optimal time), how much to bid (maximize ROAS), which clinics might churn (save them proactively).",
    },

    # ===== HEALTHCARE MARKETING SPECIFIC =====
    "healthcare_marketing_strategy": {
        "title": "Healthcare Marketing Principles (compiled)",
        "author": "Various — ICG, HealthcareSuccess, Practitioner knowledge",
        "category": "healthcare_specific",
        "key_principles": [
            "TRUST is the #1 conversion factor in healthcare — not price, not convenience",
            "Doctor's face in marketing builds trust 3x more than clinic logo",
            "Patient privacy is non-negotiable — DPDP Act 2023 compliance required",
            "NMC Oct 2026 rules: no 'best doctor', no guaranteed outcomes, no patient testimonials in ads",
            "Speed-to-lead is the #1 KPI — respond in <10 seconds, not hours",
            "WhatsApp is the #1 communication channel for Indian patients",
            "After-hours enquiries represent 30-40% of total — AI captures what humans miss",
            "Patient journey: awareness (Meta) → research (Google) → enquiry (WhatsApp) → booking (calendar) → reminder → attendance → follow-up → referral",
            "Google My Business optimization is free and drives 20-30% of leads for local clinics",
            "Video content (Reels/Shorts) is the highest-engagement format for healthcare education",
        ],
        "how_ai_uses_it": "Every campaign, every ad, every WhatsApp message is designed around these principles. The AI never violates NMC rules, always responds fast, always leads with trust.",
    },
    "india_healthcare_market": {
        "title": "India Healthcare Market Intelligence",
        "author": "Compiled from IBEF, Practo, ICG, NMC",
        "category": "market_intelligence",
        "key_principles": [
            "1.5M+ clinics in India — massive TAM",
            "~80% are solo or 2-3 doctor practices — our ICP",
            "Average clinic spends ₹0-30K/month on marketing — most spend ₹0",
            "Agency market: ₹30K-1L/month with zero transparency — our competition",
            "WhatsApp has 500M+ users in India — the default communication channel",
            "Google searches for healthcare growing 20% YoY in India",
            "Tier-2 and Tier-3 cities are the fastest-growing healthcare markets",
            "Elective procedures (dental, derma, IVF, hair transplant) are 80% of ad-driven healthcare",
            "NMC (National Medical Commission) is the regulatory body — compliance is mandatory",
            "DPDP Act 2023 = India's data protection law — patient data handling rules",
        ],
        "how_ai_uses_it": "Market sizing, ICP selection, city prioritization, regulatory compliance. The AI knows which specialties have the highest ROI and which cities are underserved.",
    },

    # ===== SALES =====
    "spin_selling": {
        "title": "SPIN Selling",
        "author": "Neil Rackham (1988)",
        "category": "sales",
        "key_principles": [
            "SPIN = Situation, Problem, Implication, Need-payoff",
            "Situation: 'How do you currently get new patients?'",
            "Problem: 'What happens when patients call after hours?'",
            "Implication: 'How much revenue do you think you lose from missed enquiries each month?'",
            "Need-payoff: 'What if every WhatsApp message was answered in 10 seconds, 24/7?'",
            "Don't pitch features — ask questions that make the doctor realize the problem",
        ],
        "how_ai_uses_it": "SDR outreach scripts and demo call structure follow SPIN. The Lead Hunter AI drafts emails that lead with Situation/Problem questions, not product features.",
    },
    "never_split_the_difference": {
        "title": "Never Split the Difference",
        "author": "Chris Voss (2016)",
        "category": "sales",
        "key_principles": [
            "Tactical empathy: understand the doctor's perspective first",
            "Mirroring: repeat their last 3 words to keep them talking",
            "Labeling: 'It sounds like you're frustrated with your current agency...'",
            "Calibrated questions: 'How am I supposed to do that?' → 'How can we make this work within your budget?'",
            "No-oriented questions: 'Would it be ridiculous to try a 14-day free trial?'",
            "The accusation audit: 'You probably think this is too good to be true...' → disarms objections",
        ],
        "how_ai_uses_it": "AI SDR outreach uses no-oriented questions and accusation audits in emails. CSM scripts use labeling and tactical empathy for retention calls.",
    },

    # ===== PRODUCT =====
    "dont_make_me_think": {
        "title": "Don't Make Me Think",
        "author": "Steve Krug (2000)",
        "category": "ux",
        "key_principles": [
            "Every page should be self-evident — zero learning curve",
            "Users scan, they don't read — use clear visual hierarchy",
            "The most important action on every page should be the most prominent",
            "For PatientPlex dashboard: the FIRST thing a doctor sees is 'New patients this month: 22'",
            "Mobile-first: 70%+ of doctors check their dashboard on mobile",
            "3-click rule: any action should take max 3 clicks/taps",
        ],
        "how_ai_uses_it": "Dashboard design, onboarding flow, and landing page layout follow Krug's principles. The AI generates landing pages with ONE clear CTA, not five options.",
    },
}


# ---------------------------------------------------------------------------
# Quick-access API
# ---------------------------------------------------------------------------

class KnowledgeLibrary:
    """Query the knowledge library for principles and frameworks."""

    def __init__(self):
        self.library = KNOWLEDGE_LIBRARY

    def get_all_books(self) -> List[Dict]:
        """List all books/frameworks in the library."""
        return [
            {
                "key": key,
                "title": book["title"],
                "author": book["author"],
                "category": book["category"],
            }
            for key, book in self.library.items()
        ]

    def get_by_category(self, category: str) -> List[Dict]:
        """Get all knowledge in a category."""
        return [
            book for book in self.library.values()
            if book["category"] == category
        ]

    def get_principles_for_task(self, task: str) -> List[str]:
        """Get relevant principles for a specific task.

        Tasks: ad_copy, bidding, nurture, sales, onboarding, retention, content, landing_page
        """
        task_to_books = {
            "ad_copy": ["scientific_advertising", "ogilvy_on_advertising", "breakthrough_advertising", "influence_cialdini"],
            "bidding": ["prediction_machines", "lean_startup", "thinking_fast_and_slow"],
            "nurture": ["influence_cialdini", "hooked_nir_eyal", "breakthrough_advertising", "never_split_the_difference"],
            "sales": ["spin_selling", "never_split_the_difference", "crossing_the_chasm"],
            "onboarding": ["dont_make_me_think", "hooked_nir_eyal"],
            "retention": ["influence_cialdini", "hooked_nir_eyal", "never_split_the_difference"],
            "content": ["ogilvy_on_advertising", "breakthrough_advertising", "healthcare_marketing_strategy"],
            "landing_page": ["dont_make_me_think", "scientific_advertising", "influence_cialdini"],
        }

        principles = []
        book_keys = task_to_books.get(task, [])
        for key in book_keys:
            if key in self.library:
                principles.extend(self.library[key]["key_principles"])
        return principles

    def get_book(self, key: str) -> Dict:
        """Get a specific book's full data."""
        return self.library.get(key, {})


# Singleton
knowledge_library = KnowledgeLibrary()
