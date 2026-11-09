"""
PatientPlex ML Engine — Machine Learning & Reinforcement Learning for healthcare marketing.

Contains:
1. Reinforcement Learning (RL) Agent — learns optimal bid/budget strategies from rewards
2. Conversion Prediction Model — predicts which leads will convert
3. Treatment Demand Forecasting — time-series prediction of treatment demand
4. Patient Lifetime Value (LTV) Model — estimates long-term value of each patient
5. Ad Creative Scorer — predicts CTR of ad copy before launch
6. Optimal Send Time Model — learns best time to send WhatsApp messages
7. Lookalike Audience Builder — finds patients similar to best converters
8. Churn Prediction Model — predicts which clinics might cancel
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging
import json
import math

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Replay Buffer for RL
# ---------------------------------------------------------------------------

@dataclass
class Experience:
    """Single experience tuple for replay buffer."""
    state: Dict
    action: Dict
    reward: float
    next_state: Dict
    done: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ReplayBuffer:
    """Fixed-capacity experience replay buffer for RL agent."""

    def __init__(self, capacity: int = 10000):
        self.buffer: List[Experience] = []
        self.capacity = capacity
        self.position = 0

    def push(self, experience: Experience):
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
        else:
            self.buffer[self.position] = experience
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size: int) -> List[Experience]:
        indices = np.random.choice(
            len(self.buffer), min(batch_size, len(self.buffer)), replace=False
        )
        return [self.buffer[i] for i in indices]

    def __len__(self):
        return len(self.buffer)


# ---------------------------------------------------------------------------
# 1. Reinforcement Learning Bidding Agent
# ---------------------------------------------------------------------------

class BiddingRLAgent:
    """
    RL agent that learns optimal bidding strategies using Q-learning.

    State space (discretised):
      current_cpc, ctr, conv_rate, budget_remaining, hour_of_day, day_of_week,
      competitor_density, quality_score, ad_position

    Action space:
      bid multiplier ∈ {0.5, 0.6, … 2.0}

    Reward:
      conversions − (cost × cost_weight)

    Uses ε-greedy exploration with decaying ε and an experience replay buffer.
    Production path: upgrade to Deep Q-Network (DQN) or PPO.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.05,
    ):
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table: Dict[str, Dict[str, float]] = {}
        self.replay_buffer = ReplayBuffer(capacity=50_000)
        self.training_steps = 0
        self.total_reward = 0.0

        # Discretised action set — bid multipliers
        self.actions = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0]

    # --- helpers ---

    def _discretize_state(self, state: Dict) -> str:
        cpc_bucket = min(int(state.get("cpc", 10) / 5), 10)
        ctr_bucket = min(int(state.get("ctr", 0.02) * 100), 10)
        conv_bucket = min(int(state.get("conv_rate", 0.05) * 20), 10)
        hour_bucket = state.get("hour", 12) // 4
        day_bucket = state.get("day_of_week", 0)
        return f"{cpc_bucket}_{ctr_bucket}_{conv_bucket}_{hour_bucket}_{day_bucket}"

    def _ensure_state(self, key: str):
        if key not in self.q_table:
            self.q_table[key] = {str(a): 0.0 for a in self.actions}

    # --- public ---

    def select_action(self, state: Dict) -> Tuple[float, bool]:
        """ε-greedy action selection. Returns (bid_multiplier, explored)."""
        if np.random.random() < self.epsilon:
            return float(np.random.choice(self.actions)), True
        state_key = self._discretize_state(state)
        self._ensure_state(state_key)
        best = max(self.q_table[state_key], key=self.q_table[state_key].get)
        return float(best), False

    def learn(
        self,
        state: Dict,
        action: float,
        reward: float,
        next_state: Dict,
        done: bool,
    ):
        """Q-learning update with experience replay storage."""
        self.replay_buffer.push(
            Experience(state, {"bid_multiplier": action}, reward, next_state, done)
        )

        state_key = self._discretize_state(state)
        action_key = str(action)
        self._ensure_state(state_key)

        next_key = self._discretize_state(next_state)
        self._ensure_state(next_key)
        max_next_q = max(self.q_table[next_key].values())

        current_q = self.q_table[state_key].get(action_key, 0.0)
        target = reward + self.gamma * max_next_q * (1 - int(done))
        self.q_table[state_key][action_key] = current_q + self.lr * (target - current_q)

        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.training_steps += 1
        self.total_reward += reward

    def batch_replay(self, batch_size: int = 32):
        """Sample from replay buffer and run multiple learning steps."""
        if len(self.replay_buffer) < batch_size:
            return
        batch = self.replay_buffer.sample(batch_size)
        for exp in batch:
            self.learn(exp.state, exp.action["bid_multiplier"], exp.reward, exp.next_state, exp.done)

    def get_stats(self) -> Dict:
        return {
            "training_steps": self.training_steps,
            "epsilon": round(self.epsilon, 4),
            "total_reward": round(self.total_reward, 2),
            "q_table_states": len(self.q_table),
            "replay_buffer_size": len(self.replay_buffer),
            "model_type": "Tabular Q-Learning",
        }


# ---------------------------------------------------------------------------
# 2. Conversion Prediction (Online Logistic Regression)
# ---------------------------------------------------------------------------

class ConversionPredictor:
    """
    Predicts P(lead → booked appointment) using online logistic regression.

    Features include source channel, response time, messages exchanged,
    returning-patient flag, distance, treatment value, time-of-day buckets,
    weekend flag, and device type.

    Weights are updated via stochastic gradient descent after each observed
    outcome, so the model improves continuously without batch retraining.
    """

    def __init__(self):
        self.weights: Dict[str, float] = {
            "source_google": 0.30,
            "source_meta": 0.25,
            "source_chatgpt": 0.35,
            "source_linkedin": 0.15,
            "source_whatsapp_organic": 0.40,
            "response_time_minutes": -0.02,
            "messages_exchanged": 0.05,
            "is_returning_patient": 0.60,
            "distance_km": -0.03,
            "treatment_value_inr": 0.0001,
            "hour_9_to_12": 0.20,
            "hour_12_to_14": 0.30,
            "hour_17_to_20": 0.25,
            "is_weekend": 0.15,
            "is_mobile": 0.10,
            "bias": -0.50,
        }
        self.learning_rate = 0.001
        self.predictions_made = 0
        self.correct_predictions = 0

    @staticmethod
    def _sigmoid(z: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, z))))

    def predict(self, features: Dict) -> float:
        z = self.weights.get("bias", 0.0)
        for key, weight in self.weights.items():
            if key != "bias" and key in features:
                z += weight * features[key]
        prob = self._sigmoid(z)
        self.predictions_made += 1
        return round(prob, 4)

    def update(self, features: Dict, actual_outcome: int):
        """Online SGD update after observing a conversion (1) or drop (0)."""
        predicted = self.predict(features)
        error = actual_outcome - predicted

        if (predicted >= 0.5) == (actual_outcome == 1):
            self.correct_predictions += 1

        for key in self.weights:
            if key == "bias":
                self.weights[key] += self.learning_rate * error
            elif key in features:
                self.weights[key] += self.learning_rate * error * features[key]

    def get_accuracy(self) -> float:
        if self.predictions_made == 0:
            return 0.0
        return round(self.correct_predictions / self.predictions_made, 4)

    def get_stats(self) -> Dict:
        return {
            "model_type": "Online Logistic Regression",
            "predictions_made": self.predictions_made,
            "accuracy": self.get_accuracy(),
            "feature_count": len(self.weights),
            "weights": {k: round(v, 4) for k, v in self.weights.items()},
        }


# ---------------------------------------------------------------------------
# 3. Patient Lifetime Value Model
# ---------------------------------------------------------------------------

class PatientLTVModel:
    """
    Estimates patient LTV by specialty using:
      LTV = (avg_visit_value × visits/year × retention_years × (1 + referral_rate × 0.5))
            − acquisition_cost
    """

    SPECIALTY_FACTORS: Dict[str, Dict] = {
        "dental":        {"avg_visit_value": 2500,   "visits_per_year": 2.5, "retention_years": 5,  "referral_rate": 0.15},
        "dermatology":   {"avg_visit_value": 3500,   "visits_per_year": 4,   "retention_years": 3,  "referral_rate": 0.20},
        "ophthalmology": {"avg_visit_value": 5000,   "visits_per_year": 1.5, "retention_years": 4,  "referral_rate": 0.10},
        "orthopedics":   {"avg_visit_value": 4000,   "visits_per_year": 3,   "retention_years": 4,  "referral_rate": 0.12},
        "gynecology":    {"avg_visit_value": 3000,   "visits_per_year": 3,   "retention_years": 6,  "referral_rate": 0.25},
        "ivf":           {"avg_visit_value": 150_000, "visits_per_year": 1,   "retention_years": 2,  "referral_rate": 0.30},
        "pediatrics":    {"avg_visit_value": 1500,   "visits_per_year": 6,   "retention_years": 8,  "referral_rate": 0.20},
        "cardiology":    {"avg_visit_value": 5000,   "visits_per_year": 2,   "retention_years": 10, "referral_rate": 0.10},
        "ent":           {"avg_visit_value": 2000,   "visits_per_year": 2,   "retention_years": 4,  "referral_rate": 0.12},
        "neurology":     {"avg_visit_value": 4500,   "visits_per_year": 2,   "retention_years": 6,  "referral_rate": 0.08},
        "psychiatry":    {"avg_visit_value": 2000,   "visits_per_year": 12,  "retention_years": 3,  "referral_rate": 0.10},
        "urology":       {"avg_visit_value": 3000,   "visits_per_year": 2,   "retention_years": 5,  "referral_rate": 0.10},
        "oncology":      {"avg_visit_value": 20_000, "visits_per_year": 6,   "retention_years": 3,  "referral_rate": 0.05},
        "gastroenterology": {"avg_visit_value": 3500,"visits_per_year": 2,   "retention_years": 5,  "referral_rate": 0.10},
        "pulmonology":   {"avg_visit_value": 3000,   "visits_per_year": 3,   "retention_years": 5,  "referral_rate": 0.08},
        "general":       {"avg_visit_value": 800,    "visits_per_year": 5,   "retention_years": 7,  "referral_rate": 0.15},
    }

    def calculate_ltv(
        self,
        specialty: str,
        treatment_value: Optional[float] = None,
        acquisition_cost: float = 12.0,
    ) -> Dict:
        factors = self.SPECIALTY_FACTORS.get(specialty, self.SPECIALTY_FACTORS["general"])
        avg_value = treatment_value or factors["avg_visit_value"]
        visits = factors["visits_per_year"]
        years = factors["retention_years"]
        referral = factors["referral_rate"]

        base_ltv = avg_value * visits * years
        referral_ltv = base_ltv * referral * 0.5
        total_ltv = base_ltv + referral_ltv - acquisition_cost
        roi = total_ltv / max(acquisition_cost, 1)

        return {
            "specialty": specialty,
            "base_ltv_inr": round(base_ltv),
            "referral_ltv_inr": round(referral_ltv),
            "total_ltv_inr": round(total_ltv),
            "acquisition_cost_inr": round(acquisition_cost),
            "roi_multiple": round(roi, 1),
            "visits_per_year": visits,
            "retention_years": years,
            "referral_rate": referral,
        }

    def compare_specialties(self) -> List[Dict]:
        """Rank all specialties by ROI."""
        results = [self.calculate_ltv(s) for s in self.SPECIALTY_FACTORS]
        return sorted(results, key=lambda r: r["roi_multiple"], reverse=True)


# ---------------------------------------------------------------------------
# 4. Treatment Demand Forecaster (Holt's Double Exponential Smoothing)
# ---------------------------------------------------------------------------

class TreatmentDemandForecaster:
    """Forecasts treatment demand using Holt's linear trend method."""

    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta

    def forecast(self, historical_data: List[float], periods_ahead: int = 3) -> Dict:
        if len(historical_data) < 3:
            avg = sum(historical_data) / max(len(historical_data), 1)
            return {
                "forecast": [round(avg)] * periods_ahead,
                "confidence": "low",
                "trend": "insufficient_data",
            }

        level = historical_data[0]
        trend = historical_data[1] - historical_data[0]

        for val in historical_data[1:]:
            prev_level = level
            level = self.alpha * val + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - prev_level) + (1 - self.beta) * trend

        forecasts = [round(level + trend * i) for i in range(1, periods_ahead + 1)]

        if trend > 1:
            trend_dir = "growing"
        elif trend < -1:
            trend_dir = "declining"
        else:
            trend_dir = "stable"

        return {
            "forecast": forecasts,
            "trend": trend_dir,
            "trend_value": round(trend, 2),
            "confidence": "high" if len(historical_data) >= 12 else "medium",
            "last_actual": historical_data[-1],
            "model_type": "Holt Double Exponential Smoothing",
        }


# ---------------------------------------------------------------------------
# 5. Optimal Send Time (Thompson Sampling Multi-Armed Bandit)
# ---------------------------------------------------------------------------

class OptimalSendTimeModel:
    """
    Learns the best hour to send WhatsApp messages for maximum engagement
    using Thompson Sampling with Beta priors.
    """

    def __init__(self):
        self.successes = [1] * 24  # Beta(α, β) prior
        self.failures = [1] * 24
        self.total_sends = 0

    def get_best_hour(self) -> Dict:
        samples = [np.random.beta(self.successes[h], self.failures[h]) for h in range(24)]
        best_hour = int(np.argmax(samples))
        ranked = sorted(range(24), key=lambda h: samples[h], reverse=True)
        top_3 = [{"hour": h, "formatted": f"{h:02d}:00", "score": round(samples[h], 3)} for h in ranked[:3]]
        return {
            "best_hour": best_hour,
            "best_hour_formatted": f"{best_hour:02d}:00",
            "top_3_hours": top_3,
            "total_data_points": self.total_sends,
            "model_type": "Thompson Sampling Bandit",
        }

    def update(self, hour: int, engaged: bool):
        if engaged:
            self.successes[hour] += 1
        else:
            self.failures[hour] += 1
        self.total_sends += 1


# ---------------------------------------------------------------------------
# 6. Ad Creative Scorer
# ---------------------------------------------------------------------------

class AdCreativeScorer:
    """Predicts CTR of ad copy before launch using feature-based scoring."""

    POWER_WORDS = frozenset({
        "free", "instant", "guaranteed", "proven", "exclusive", "limited",
        "painless", "affordable", "expert", "trusted", "advanced", "best",
        "certified", "safe", "quick", "easy", "discount", "offer", "today",
    })
    URGENCY_WORDS = frozenset({
        "now", "today", "limited", "hurry", "last", "ending", "urgent",
        "immediately", "fast", "quick", "book now", "call now",
    })
    CTA_WORDS = frozenset({"book", "call", "visit", "schedule", "consult", "enquire", "get"})
    LOCATION_WORDS = frozenset({"near", "km", "local", "city", "area", "nearby"})

    def score(self, headline: str, description: str, treatment: str = "") -> Dict:
        h_lower = headline.lower()
        d_lower = description.lower()
        combined = f"{h_lower} {d_lower}"

        score = 50
        factors: List[str] = []

        # Headline length
        h_len = len(headline)
        if 30 <= h_len <= 60:
            score += 10; factors.append("Good headline length")
        elif h_len < 20:
            score -= 10; factors.append("Headline too short")
        elif h_len > 80:
            score -= 5; factors.append("Headline too long")

        # Power words
        pw = sum(1 for w in self.POWER_WORDS if w in combined)
        if pw:
            score += min(pw * 5, 15); factors.append(f"{pw} power word(s)")

        # Numbers
        if any(c.isdigit() for c in headline):
            score += 8; factors.append("Contains numbers (good for CTR)")

        # Urgency
        uw = sum(1 for w in self.URGENCY_WORDS if w in combined)
        if uw:
            score += min(uw * 4, 12); factors.append("Contains urgency words")

        # Price / offer
        if "₹" in combined or "free" in combined or "rs" in combined:
            score += 7; factors.append("Price/offer mentioned")

        # Treatment relevance
        if treatment and treatment.lower() in combined:
            score += 10; factors.append("Treatment mentioned in copy")

        # CTA
        if any(w in combined for w in self.CTA_WORDS):
            score += 8; factors.append("Clear CTA present")

        # Location
        if any(w in combined for w in self.LOCATION_WORDS):
            score += 5; factors.append("Location relevance")

        score = max(0, min(100, score))
        predicted_ctr = round(0.5 + (score / 100) * 4.5, 2)

        return {
            "score": score,
            "predicted_ctr_percent": predicted_ctr,
            "rating": (
                "Excellent" if score >= 80 else
                "Good" if score >= 60 else
                "Average" if score >= 40 else
                "Needs work"
            ),
            "factors": factors,
            "recommendations": self._recommendations(headline, combined),
        }

    def _recommendations(self, headline: str, combined: str) -> List[str]:
        recs = []
        if not any(c.isdigit() for c in headline):
            recs.append("Add a number to your headline (e.g. '50% off' or '₹999')")
        if not any(w in combined for w in self.URGENCY_WORDS):
            recs.append("Add urgency (e.g. 'Book today' or 'Limited slots')")
        if "₹" not in combined:
            recs.append("Consider mentioning price or an offer")
        if len(headline) < 25:
            recs.append("Make your headline longer and more descriptive")
        return recs


# ---------------------------------------------------------------------------
# 7. Lookalike Audience Builder
# ---------------------------------------------------------------------------

class LookalikeAudienceBuilder:
    """
    Builds lookalike audiences by finding patients similar to best converters.
    Uses cosine similarity on normalised feature vectors.
    """

    @staticmethod
    def _normalise(vec: List[float]) -> np.ndarray:
        a = np.array(vec, dtype=float)
        norm = np.linalg.norm(a)
        return a / norm if norm > 0 else a

    def find_similar(
        self,
        seed_profiles: List[Dict],
        candidate_profiles: List[Dict],
        features: List[str],
        top_n: int = 10,
    ) -> List[Dict]:
        """
        Given seed profiles (best converters) and candidates, return top_n
        candidates ranked by similarity.
        """
        if not seed_profiles or not candidate_profiles:
            return []

        # Compute centroid of seed profiles
        seed_vectors = []
        for p in seed_profiles:
            seed_vectors.append([p.get(f, 0) for f in features])
        centroid = self._normalise(np.mean(seed_vectors, axis=0).tolist())

        # Score candidates
        scored = []
        for p in candidate_profiles:
            vec = self._normalise([p.get(f, 0) for f in features])
            sim = float(np.dot(centroid, vec))
            scored.append({**p, "similarity_score": round(sim, 4)})

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_n]


# ---------------------------------------------------------------------------
# 8. Clinic Churn Predictor
# ---------------------------------------------------------------------------

class ClinicChurnPredictor:
    """
    Predicts probability that a clinic will churn (cancel subscription)
    based on engagement signals.

    Features: days_since_last_login, ads_running, avg_monthly_spend,
              support_tickets_open, months_subscribed, appointments_booked_30d.
    """

    def __init__(self):
        self.weights: Dict[str, float] = {
            "days_since_last_login": 0.04,
            "ads_running": -0.5,
            "avg_monthly_spend_inr": -0.0002,
            "support_tickets_open": 0.15,
            "months_subscribed": -0.03,
            "appointments_booked_30d": -0.08,
            "bias": 0.3,
        }

    def predict(self, features: Dict) -> Dict:
        z = self.weights.get("bias", 0.0)
        for key, w in self.weights.items():
            if key != "bias" and key in features:
                z += w * features[key]
        prob = 1.0 / (1.0 + math.exp(-max(-10, min(10, z))))
        risk = "high" if prob >= 0.7 else "medium" if prob >= 0.4 else "low"
        return {
            "churn_probability": round(prob, 4),
            "risk_level": risk,
            "top_factors": self._top_factors(features),
        }

    def _top_factors(self, features: Dict) -> List[str]:
        factors = []
        if features.get("days_since_last_login", 0) > 14:
            factors.append("Inactive for over 2 weeks")
        if features.get("ads_running", 1) == 0:
            factors.append("No active ad campaigns")
        if features.get("appointments_booked_30d", 5) < 3:
            factors.append("Very few appointments booked recently")
        if features.get("support_tickets_open", 0) >= 3:
            factors.append("Multiple open support tickets")
        return factors


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class MLEngine:
    """Central orchestrator for all ML models."""

    def __init__(self):
        self.bidding_agent = BiddingRLAgent()
        self.conversion_predictor = ConversionPredictor()
        self.ltv_model = PatientLTVModel()
        self.demand_forecaster = TreatmentDemandForecaster()
        self.send_time_model = OptimalSendTimeModel()
        self.creative_scorer = AdCreativeScorer()
        self.lookalike_builder = LookalikeAudienceBuilder()
        self.churn_predictor = ClinicChurnPredictor()

    def get_all_model_stats(self) -> Dict:
        return {
            "engine": "PatientPlex ML Engine v1.0",
            "models_active": 8,
            "bidding_rl_agent": self.bidding_agent.get_stats(),
            "conversion_predictor": self.conversion_predictor.get_stats(),
            "send_time_model": self.send_time_model.get_best_hour(),
            "total_training_steps": self.bidding_agent.training_steps,
            "total_predictions": self.conversion_predictor.predictions_made,
            "capabilities": [
                "Reinforcement Learning bid optimization",
                "Lead conversion prediction",
                "Patient lifetime value estimation",
                "Treatment demand forecasting",
                "Optimal WhatsApp send-time learning",
                "Ad creative CTR prediction",
                "Lookalike audience building",
                "Clinic churn prediction",
            ],
        }
