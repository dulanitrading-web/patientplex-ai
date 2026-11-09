"""Marketing Brain API — endpoints for the AI marketing orchestrator."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.marketing_brain import MarketingBrain

router = APIRouter(prefix="/marketing-brain", tags=["marketing-brain"])

brain = MarketingBrain()


@router.get("/health-score/{doctor_id}")
async def clinic_health_score(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Get the overall marketing health score for a clinic."""
    return await brain.get_clinic_health_score(doctor_id, db)


@router.post("/optimize-budget/{doctor_id}")
async def optimize_budget(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Run budget allocation optimization across all ad channels."""
    return await brain.optimize_budget_allocation(doctor_id, db)


@router.get("/patient-persona/{doctor_id}")
async def patient_persona(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Get the AI-built patient persona for targeting."""
    return await brain.build_patient_persona(doctor_id, db)


@router.post("/optimize-bids/{doctor_id}")
async def optimize_bids(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Run real-time bid optimization."""
    return await brain.optimize_bids(doctor_id, db)


@router.post("/optimize-creatives/{doctor_id}/{campaign_id}")
async def optimize_creatives(doctor_id: int, campaign_id: int, db: AsyncSession = Depends(get_db)):
    """Run creative A/B test optimization for a campaign."""
    return await brain.optimize_creatives(doctor_id, campaign_id, db)


@router.get("/anomalies/{doctor_id}")
async def detect_anomalies(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Detect performance anomalies across all channels."""
    return await brain.detect_anomalies(doctor_id, db)


@router.get("/competitors/{doctor_id}")
async def analyze_competitors(
    doctor_id: int,
    location: str = "Mumbai",
    specialty: str = "dental",
    db: AsyncSession = Depends(get_db),
):
    """Analyze competitor ad strategies in the local market."""
    return await brain.analyze_competitors(doctor_id, location, specialty, db)


@router.get("/forecast/{doctor_id}")
async def forecast(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Predict next month's patient volume and revenue."""
    return await brain.predict_monthly_performance(doctor_id, db)


@router.post("/daily-optimization/{doctor_id}")
async def daily_optimization(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Run the full daily optimization cycle."""
    return await brain.run_daily_optimization(doctor_id, db)


@router.post("/patient-journey/{doctor_id}")
async def patient_journey(doctor_id: int, phone: str, db: AsyncSession = Depends(get_db)):
    """Orchestrate the patient journey across all channels."""
    return await brain.orchestrate_patient_journey(doctor_id, phone, db)
