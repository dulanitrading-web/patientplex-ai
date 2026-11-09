"""Tests for ML API endpoints using a sync TestClient (no DB needed for ML routes)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestMLStatsEndpoint:
    def test_ml_stats(self):
        response = client.get("/api/v1/ml/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["models_active"] == 8
        assert "bidding_rl_agent" in data
        assert "conversion_predictor" in data
        assert "capabilities" in data


class TestConversionEndpoints:
    def test_predict_conversion(self):
        response = client.post("/api/v1/ml/predict-conversion", json={
            "source_google": 1,
            "response_time_minutes": 3,
            "messages_exchanged": 2,
        })
        assert response.status_code == 200
        data = response.json()
        assert "conversion_probability" in data
        assert 0 <= data["conversion_probability"] <= 1

    def test_predict_conversion_defaults(self):
        response = client.post("/api/v1/ml/predict-conversion", json={})
        assert response.status_code == 200

    def test_train_conversion(self):
        response = client.post("/api/v1/ml/train-conversion", json={
            "features": {"source_google": 1, "response_time_minutes": 2},
            "converted": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] is True


class TestCreativeScoreEndpoint:
    def test_score_creative(self):
        response = client.post("/api/v1/ml/score-creative", json={
            "headline": "Best Dental Care in Mumbai - Book Now!",
            "description": "Expert teeth whitening at ₹999. Call today.",
            "treatment": "teeth whitening",
        })
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "predicted_ctr_percent" in data
        assert "rating" in data
        assert "factors" in data

    def test_score_creative_minimal(self):
        response = client.post("/api/v1/ml/score-creative", json={
            "headline": "Hi",
            "description": "Visit",
        })
        assert response.status_code == 200


class TestLTVEndpoints:
    def test_ltv_dental(self):
        response = client.get("/api/v1/ml/ltv/dental")
        assert response.status_code == 200
        data = response.json()
        assert data["specialty"] == "dental"
        assert data["total_ltv_inr"] > 0
        assert data["roi_multiple"] > 0

    def test_ltv_unknown_specialty(self):
        response = client.get("/api/v1/ml/ltv/unknown_xyz")
        assert response.status_code == 200

    def test_ltv_with_custom_params(self):
        response = client.get("/api/v1/ml/ltv/dental?treatment_value=10000&acquisition_cost=500")
        assert response.status_code == 200

    def test_ltv_compare(self):
        response = client.get("/api/v1/ml/ltv-compare")
        assert response.status_code == 200
        data = response.json()
        assert "specialties" in data


class TestForecastEndpoint:
    def test_forecast_demand(self):
        response = client.post("/api/v1/ml/forecast-demand", json={
            "historical_data": [100, 110, 120, 130, 140, 150],
            "periods_ahead": 3,
        })
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert len(data["forecast"]) == 3

    def test_forecast_validation_empty(self):
        response = client.post("/api/v1/ml/forecast-demand", json={
            "historical_data": [],
            "periods_ahead": 3,
        })
        assert response.status_code == 422  # validation error: min_length=1


class TestSendTimeEndpoints:
    def test_optimal_send_time(self):
        response = client.get("/api/v1/ml/optimal-send-time")
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["best_hour"] <= 23
        assert "top_3_hours" in data

    def test_update_send_time(self):
        response = client.post("/api/v1/ml/update-send-time", json={
            "hour": 10,
            "engaged": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] is True


class TestBiddingEndpoints:
    def test_select_action(self):
        response = client.post("/api/v1/ml/bidding/select-action", json={
            "cpc": 10,
            "ctr": 0.03,
            "conv_rate": 0.05,
            "hour": 14,
            "day_of_week": 2,
        })
        assert response.status_code == 200
        data = response.json()
        assert "bid_multiplier" in data
        assert 0.5 <= data["bid_multiplier"] <= 2.0
        assert "explored" in data

    def test_bidding_learn(self):
        response = client.post("/api/v1/ml/bidding/learn", json={
            "state": {"cpc": 10, "ctr": 0.03, "conv_rate": 0.05, "hour": 14, "day_of_week": 2},
            "action": 1.2,
            "reward": 3.5,
            "next_state": {"cpc": 9, "ctr": 0.035, "conv_rate": 0.06, "hour": 15, "day_of_week": 2},
            "done": False,
        })
        assert response.status_code == 200
        data = response.json()
        assert "training_steps" in data


class TestChurnEndpoint:
    def test_predict_churn(self):
        response = client.post("/api/v1/ml/predict-churn", json={
            "days_since_last_login": 5,
            "ads_running": 1,
            "avg_monthly_spend_inr": 5000,
            "support_tickets_open": 0,
            "months_subscribed": 6,
            "appointments_booked_30d": 10,
        })
        assert response.status_code == 200
        data = response.json()
        assert "churn_probability" in data
        assert "risk_level" in data


class TestLookalikeEndpoint:
    def test_lookalike_audience(self):
        response = client.post("/api/v1/ml/lookalike-audience", json={
            "seed_profiles": [{"age": 30, "spend": 5000}],
            "candidate_profiles": [
                {"age": 32, "spend": 5500},
                {"age": 60, "spend": 500},
            ],
            "features": ["age", "spend"],
            "top_n": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert data["count"] >= 0
