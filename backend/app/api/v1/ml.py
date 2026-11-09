"""Machine Learning API endpoints."""

from typing import Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.ml_engine import MLEngine

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Singleton engine instance
_engine = MLEngine()


# --- request models ---

class ConversionFeatures(BaseModel):
    source_google: float = 0
    source_meta: float = 0
    source_chatgpt: float = 0
    source_linkedin: float = 0
    source_whatsapp_organic: float = 0
    response_time_minutes: float = 5
    messages_exchanged: float = 3
    is_returning_patient: float = 0
    distance_km: float = 5
    treatment_value_inr: float = 2000
    hour_9_to_12: float = 0
    hour_12_to_14: float = 0
    hour_17_to_20: float = 0
    is_weekend: float = 0
    is_mobile: float = 1


class ConversionOutcome(BaseModel):
    features: ConversionFeatures
    converted: int = Field(..., ge=0, le=1)


class CreativeInput(BaseModel):
    headline: str
    description: str
    treatment: str = ""


class ForecastInput(BaseModel):
    historical_data: List[float] = Field(..., min_length=1)
    periods_ahead: int = Field(3, ge=1, le=24)


class BiddingState(BaseModel):
    cpc: float = 10
    ctr: float = 0.02
    conv_rate: float = 0.05
    hour: int = 12
    day_of_week: int = 1


class BiddingExperience(BaseModel):
    state: BiddingState
    action: float
    reward: float
    next_state: BiddingState
    done: bool = False


class SendTimeUpdate(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    engaged: bool


class ChurnFeatures(BaseModel):
    days_since_last_login: float = 0
    ads_running: float = 1
    avg_monthly_spend_inr: float = 5000
    support_tickets_open: float = 0
    months_subscribed: float = 6
    appointments_booked_30d: float = 10


class LookalikeRequest(BaseModel):
    seed_profiles: List[Dict]
    candidate_profiles: List[Dict]
    features: List[str]
    top_n: int = 10


# --- endpoints ---

@router.get("/stats")
async def get_ml_stats():
    """Get stats and status for all 8 ML models."""
    return _engine.get_all_model_stats()


@router.post("/predict-conversion")
async def predict_conversion(body: ConversionFeatures):
    """Predict probability a lead converts to a booked appointment."""
    features = body.model_dump()
    prob = _engine.conversion_predictor.predict(features)
    return {"conversion_probability": prob, "model": "online_logistic_regression"}


@router.post("/train-conversion")
async def train_conversion(body: ConversionOutcome):
    """Feed an observed outcome back to update the conversion model online."""
    features = body.features.model_dump()
    _engine.conversion_predictor.update(features, body.converted)
    return {
        "updated": True,
        "accuracy": _engine.conversion_predictor.get_accuracy(),
        "predictions_made": _engine.conversion_predictor.predictions_made,
    }


@router.post("/score-creative")
async def score_creative(body: CreativeInput):
    """Score ad creative copy and predict CTR before launch."""
    return _engine.creative_scorer.score(body.headline, body.description, body.treatment)


@router.get("/ltv/{specialty}")
async def calculate_ltv(
    specialty: str,
    treatment_value: Optional[float] = Query(None),
    acquisition_cost: float = Query(12),
):
    """Calculate patient lifetime value for a given specialty."""
    return _engine.ltv_model.calculate_ltv(specialty, treatment_value, acquisition_cost)


@router.get("/ltv-compare")
async def compare_ltv():
    """Compare patient LTV across all specialties, ranked by ROI."""
    return {"specialties": _engine.ltv_model.compare_specialties()}


@router.post("/forecast-demand")
async def forecast_demand(body: ForecastInput):
    """Forecast treatment demand from historical time-series data."""
    return _engine.demand_forecaster.forecast(body.historical_data, body.periods_ahead)


@router.get("/optimal-send-time")
async def get_optimal_send_time():
    """Get the best hour to send WhatsApp messages (Thompson Sampling)."""
    return _engine.send_time_model.get_best_hour()


@router.post("/update-send-time")
async def update_send_time(body: SendTimeUpdate):
    """Update the send-time model with an engagement observation."""
    _engine.send_time_model.update(body.hour, body.engaged)
    return {"updated": True, "total_data_points": _engine.send_time_model.total_sends}


@router.post("/bidding/select-action")
async def select_bidding_action(body: BiddingState):
    """RL agent selects a bid multiplier given current state."""
    state = body.model_dump()
    action, explored = _engine.bidding_agent.select_action(state)
    return {
        "bid_multiplier": action,
        "explored": explored,
        "epsilon": round(_engine.bidding_agent.epsilon, 4),
    }


@router.post("/bidding/learn")
async def bidding_learn(body: BiddingExperience):
    """Feed a reward signal back to the RL bidding agent."""
    _engine.bidding_agent.learn(
        body.state.model_dump(), body.action, body.reward,
        body.next_state.model_dump(), body.done,
    )
    return {"training_steps": _engine.bidding_agent.training_steps}


@router.post("/bidding/replay")
async def bidding_replay(batch_size: int = Query(32, ge=1, le=256)):
    """Run a batch replay training step on the RL agent."""
    _engine.bidding_agent.batch_replay(batch_size)
    return _engine.bidding_agent.get_stats()


@router.post("/predict-churn")
async def predict_churn(body: ChurnFeatures):
    """Predict probability a clinic will churn."""
    return _engine.churn_predictor.predict(body.model_dump())


@router.post("/lookalike-audience")
async def build_lookalike(body: LookalikeRequest):
    """Find candidates most similar to seed (best-converting) profiles."""
    results = _engine.lookalike_builder.find_similar(
        body.seed_profiles, body.candidate_profiles, body.features, body.top_n,
    )
    return {"matches": results, "count": len(results)}
