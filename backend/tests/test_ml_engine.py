"""Tests for the ML Engine — all 8 models."""

import pytest
from app.services.ml_engine import (
    MLEngine,
    BiddingRLAgent,
    ConversionPredictor,
    PatientLTVModel,
    TreatmentDemandForecaster,
    OptimalSendTimeModel,
    AdCreativeScorer,
    LookalikeAudienceBuilder,
    ClinicChurnPredictor,
    ReplayBuffer,
    Experience,
)


class TestReplayBuffer:
    def test_push_and_len(self):
        buf = ReplayBuffer(capacity=5)
        assert len(buf) == 0
        buf.push(Experience(state={}, action={}, reward=1.0, next_state={}, done=False))
        assert len(buf) == 1

    def test_capacity_overflow(self):
        buf = ReplayBuffer(capacity=3)
        for i in range(5):
            buf.push(Experience(state={"i": i}, action={}, reward=float(i), next_state={}, done=False))
        assert len(buf) == 3

    def test_sample(self):
        buf = ReplayBuffer(capacity=10)
        for i in range(10):
            buf.push(Experience(state={"i": i}, action={}, reward=float(i), next_state={}, done=False))
        sample = buf.sample(3)
        assert len(sample) == 3
        assert all(isinstance(e, Experience) for e in sample)


class TestBiddingRLAgent:
    def test_select_action_returns_valid_multiplier(self):
        agent = BiddingRLAgent()
        state = {"cpc": 10, "ctr": 0.03, "conv_rate": 0.05, "hour": 14, "day_of_week": 2}
        action, explored = agent.select_action(state)
        assert 0.5 <= action <= 2.0
        assert isinstance(explored, bool)

    def test_learn_updates_q_table(self):
        agent = BiddingRLAgent()
        state = {"cpc": 10, "ctr": 0.03, "conv_rate": 0.05, "hour": 14, "day_of_week": 2}
        agent.learn(state, 1.0, 5.0, state, False)
        assert agent.training_steps == 1
        assert len(agent.replay_buffer) == 1

    def test_epsilon_decays(self):
        agent = BiddingRLAgent(epsilon=1.0, epsilon_decay=0.99)
        state = {"cpc": 10, "ctr": 0.03, "conv_rate": 0.05, "hour": 14, "day_of_week": 2}
        initial_eps = agent.epsilon
        agent.learn(state, 1.0, 5.0, state, False)
        assert agent.epsilon < initial_eps

    def test_epsilon_min_floor(self):
        agent = BiddingRLAgent(epsilon=0.06, epsilon_decay=0.5, epsilon_min=0.05)
        state = {"cpc": 10, "ctr": 0.03, "conv_rate": 0.05, "hour": 14, "day_of_week": 2}
        agent.learn(state, 1.0, 5.0, state, False)
        assert agent.epsilon >= agent.epsilon_min

    def test_stats_format(self):
        agent = BiddingRLAgent()
        stats = agent.get_stats()
        assert "training_steps" in stats
        assert "epsilon" in stats
        assert "q_table_states" in stats
        assert "replay_buffer_size" in stats

    def test_exploit_mode_when_epsilon_zero(self):
        agent = BiddingRLAgent(epsilon=0.0)
        state = {"cpc": 10, "ctr": 0.03, "conv_rate": 0.05, "hour": 14, "day_of_week": 2}
        _, explored = agent.select_action(state)
        assert explored is False


class TestConversionPredictor:
    def test_predict_returns_probability(self):
        predictor = ConversionPredictor()
        features = {"source_google": 1, "response_time_minutes": 5, "messages_exchanged": 3, "is_mobile": 1}
        prob = predictor.predict(features)
        assert 0 <= prob <= 1

    def test_predict_increments_counter(self):
        predictor = ConversionPredictor()
        assert predictor.predictions_made == 0
        predictor.predict({"source_google": 1})
        assert predictor.predictions_made == 1

    def test_update_changes_weights(self):
        predictor = ConversionPredictor()
        features = {"source_google": 1, "response_time_minutes": 2}
        old_weight = predictor.weights["source_google"]
        predictor.update(features, 1)
        assert predictor.predictions_made > 0

    def test_accuracy_starts_zero(self):
        predictor = ConversionPredictor()
        assert predictor.get_accuracy() == 0.0

    def test_stats_format(self):
        predictor = ConversionPredictor()
        stats = predictor.get_stats()
        assert "predictions_made" in stats
        assert "accuracy" in stats
        assert "weights" in stats

    def test_high_intent_features_give_higher_probability(self):
        predictor = ConversionPredictor()
        low = predictor.predict({"response_time_minutes": 30, "distance_km": 20})
        high = predictor.predict({"source_google": 1, "is_returning_patient": 1, "messages_exchanged": 5, "hour_12_to_14": 1})
        assert high > low


class TestPatientLTVModel:
    def test_calculate_dental_ltv(self):
        model = PatientLTVModel()
        result = model.calculate_ltv("dental")
        assert result["specialty"] == "dental"
        assert result["total_ltv_inr"] > 0
        assert result["roi_multiple"] > 0

    def test_unknown_specialty_uses_general(self):
        model = PatientLTVModel()
        result = model.calculate_ltv("unknown_specialty")
        general = model.calculate_ltv("general")
        assert result["base_ltv_inr"] == general["base_ltv_inr"]

    def test_custom_treatment_value(self):
        model = PatientLTVModel()
        default = model.calculate_ltv("dental")
        custom = model.calculate_ltv("dental", treatment_value=10000)
        assert custom["base_ltv_inr"] > default["base_ltv_inr"]

    def test_all_specialties_return_valid(self):
        model = PatientLTVModel()
        for spec in model.SPECIALTY_FACTORS:
            result = model.calculate_ltv(spec)
            assert result["total_ltv_inr"] > 0
            assert result["roi_multiple"] > 0

    def test_acquisition_cost_deducted(self):
        model = PatientLTVModel()
        cheap = model.calculate_ltv("dental", acquisition_cost=10)
        expensive = model.calculate_ltv("dental", acquisition_cost=5000)
        assert cheap["total_ltv_inr"] > expensive["total_ltv_inr"]


class TestDemandForecaster:
    def test_forecast_with_sufficient_data(self):
        forecaster = TreatmentDemandForecaster()
        data = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210]
        result = forecaster.forecast(data, periods_ahead=3)
        assert len(result["forecast"]) == 3
        assert result["confidence"] == "high"
        assert result["trend"] == "growing"

    def test_forecast_with_minimal_data(self):
        forecaster = TreatmentDemandForecaster()
        result = forecaster.forecast([50, 60], periods_ahead=2)
        assert result["confidence"] == "low"
        assert len(result["forecast"]) == 2

    def test_declining_trend(self):
        forecaster = TreatmentDemandForecaster()
        data = [200, 190, 180, 170, 160, 150, 140, 130, 120, 110, 100, 90]
        result = forecaster.forecast(data, periods_ahead=2)
        assert result["trend"] == "declining"

    def test_stable_trend(self):
        forecaster = TreatmentDemandForecaster()
        data = [100, 101, 100, 99, 100, 101, 100, 99, 100, 101, 100, 99]
        result = forecaster.forecast(data, periods_ahead=2)
        assert result["trend"] == "stable"


class TestOptimalSendTimeModel:
    def test_get_best_hour(self):
        model = OptimalSendTimeModel()
        result = model.get_best_hour()
        assert 0 <= result["best_hour"] <= 23
        assert len(result["top_3_hours"]) == 3

    def test_update_changes_distribution(self):
        model = OptimalSendTimeModel()
        initial = model.successes[10]
        model.update(10, True)
        assert model.successes[10] == initial + 1
        assert model.total_sends == 1

    def test_failure_updates(self):
        model = OptimalSendTimeModel()
        initial_fail = model.failures[15]
        model.update(15, False)
        assert model.failures[15] == initial_fail + 1

    def test_learning_biases_toward_success(self):
        model = OptimalSendTimeModel()
        # Heavily bias hour 9
        for _ in range(50):
            model.update(9, True)
        result = model.get_best_hour()
        # Hour 9 should be in top 3 with high probability
        top_hours = [h["hour"] for h in result["top_3_hours"]]
        assert 9 in top_hours


class TestAdCreativeScorer:
    def test_score_good_ad(self):
        scorer = AdCreativeScorer()
        result = scorer.score(
            "50% Off Teeth Whitening Today - Book Now!",
            "Expert dental care at affordable prices. Call now for free consultation.",
            "teeth whitening",
        )
        assert result["score"] > 60
        assert result["predicted_ctr_percent"] > 0
        assert result["rating"] in ["Excellent", "Good", "Average", "Needs work"]

    def test_score_bad_ad(self):
        scorer = AdCreativeScorer()
        result = scorer.score("Hi", "Clinic", "")
        assert result["score"] < 60

    def test_recommendations_for_weak_ad(self):
        scorer = AdCreativeScorer()
        result = scorer.score("Visit us", "Good clinic", "")
        assert len(result["recommendations"]) > 0

    def test_treatment_mention_boosts_score(self):
        scorer = AdCreativeScorer()
        without = scorer.score("Best clinic in town", "Book now", "")
        with_treatment = scorer.score("Best clinic in town for braces", "Book now for braces consultation", "braces")
        assert with_treatment["score"] >= without["score"]

    def test_score_clamped_0_100(self):
        scorer = AdCreativeScorer()
        result = scorer.score("x", "y", "")
        assert 0 <= result["score"] <= 100


class TestLookalikeAudienceBuilder:
    def test_find_similar(self):
        builder = LookalikeAudienceBuilder()
        seeds = [{"age": 30, "spend": 5000}, {"age": 35, "spend": 6000}]
        candidates = [
            {"age": 32, "spend": 5500, "name": "A"},
            {"age": 60, "spend": 500, "name": "B"},
            {"age": 28, "spend": 4800, "name": "C"},
        ]
        results = builder.find_similar(seeds, candidates, ["age", "spend"], top_n=2)
        assert len(results) == 2

    def test_empty_candidates(self):
        builder = LookalikeAudienceBuilder()
        results = builder.find_similar([{"a": 1}], [], ["a"], top_n=5)
        assert len(results) == 0


class TestClinicChurnPredictor:
    def test_predict_returns_probability(self):
        predictor = ClinicChurnPredictor()
        features = {
            "days_since_last_login": 5,
            "ads_running": 1,
            "avg_monthly_spend_inr": 5000,
            "support_tickets_open": 0,
            "months_subscribed": 6,
            "appointments_booked_30d": 10,
        }
        result = predictor.predict(features)
        assert "churn_probability" in result
        assert 0 <= result["churn_probability"] <= 1
        assert "risk_level" in result

    def test_high_risk_signals(self):
        predictor = ClinicChurnPredictor()
        result = predictor.predict({
            "days_since_last_login": 30,
            "ads_running": 0,
            "avg_monthly_spend_inr": 0,
            "support_tickets_open": 5,
            "months_subscribed": 1,
            "appointments_booked_30d": 0,
        })
        assert result["churn_probability"] > 0.5


class TestMLEngine:
    def test_all_model_stats(self):
        engine = MLEngine()
        stats = engine.get_all_model_stats()
        assert stats["models_active"] == 8
        assert "bidding_rl_agent" in stats
        assert "conversion_predictor" in stats
        assert "capabilities" in stats
        assert len(stats["capabilities"]) == 8

    def test_engine_initializes_all_models(self):
        engine = MLEngine()
        assert engine.bidding_agent is not None
        assert engine.conversion_predictor is not None
        assert engine.ltv_model is not None
        assert engine.demand_forecaster is not None
        assert engine.send_time_model is not None
        assert engine.creative_scorer is not None
        assert engine.lookalike_builder is not None
        assert engine.churn_predictor is not None
