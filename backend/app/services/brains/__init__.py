"""
PatientPlex AI — Platform-specific Master Brains.

Each brain is a specialist that deeply understands one ad platform
and can run it like a senior performance marketer who ONLY does
that platform for healthcare clinics.

- GoogleAdsBrain: Search campaigns, keywords, bidding, quality score
- MetaAdsBrain: Audience targeting, lookalikes, creative optimization
- OrchestrationBrain: Coordinates all brains, allocates cross-platform budget
"""

from app.services.brains.google_ads_brain import GoogleAdsBrain
from app.services.brains.meta_ads_brain import MetaAdsBrain
from app.services.brains.orchestration_brain import OrchestrationBrain

__all__ = ["GoogleAdsBrain", "MetaAdsBrain", "OrchestrationBrain"]
