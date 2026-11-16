"""
PatientPlex AI — Platform-specific Master Brains.

Each brain is a specialist that deeply understands one ad platform
and can run it like a senior performance marketer who ONLY does
that platform for healthcare clinics.

- CampaignIntelligence: The MASTER brain — decides networks, bids, budgets, keywords
- GoogleAdsBrain: Search campaigns, keywords, bidding, quality score
- MetaAdsBrain: Audience targeting, lookalikes, creative optimization
- OrchestrationBrain: Coordinates all brains, allocates cross-platform budget
"""

from app.services.brains.campaign_intelligence import CampaignIntelligence, campaign_intelligence
from app.services.brains.google_ads_brain import GoogleAdsBrain
from app.services.brains.meta_ads_brain import MetaAdsBrain
from app.services.brains.orchestration_brain import OrchestrationBrain

__all__ = [
    "CampaignIntelligence",
    "campaign_intelligence",
    "GoogleAdsBrain",
    "MetaAdsBrain",
    "OrchestrationBrain",
]
