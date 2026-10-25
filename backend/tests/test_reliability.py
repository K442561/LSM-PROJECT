"""Tests for Monte Carlo simulation, On-Time Probability, and Reliability Scoring."""

import pytest
from app.reliability import (
    run_monte_carlo_simulation,
    calculate_reliability_score,
    evaluate_route_reliability,
)
from app.config import settings


def test_monte_carlo_generous_deadline():
    """Verify OTP is 100% when deadline provides ample buffer."""
    # 60 minute trip, 10 min spread, 120 min deadline
    sim = run_monte_carlo_simulation(
        base_duration_min=60.0,
        variability_std_min=10.0,
        waiting_time_min=5.0,
        current_time_min=480,   # 08:00
        deadline_min=600,       # 10:00 (120 mins available)
        num_runs=1000,
    )
    assert sim["on_time_probability"] == 100.0
    assert sim["buffer_min"] > 50.0
    assert sim["p90_duration_min"] >= sim["expected_duration_min"]


def test_monte_carlo_tight_deadline():
    """Verify OTP is 0% when deadline is physically unreachable."""
    # 90 minute trip, deadline only 40 minutes away
    sim = run_monte_carlo_simulation(
        base_duration_min=90.0,
        variability_std_min=12.0,
        waiting_time_min=10.0,
        current_time_min=480,  # 08:00
        deadline_min=520,      # 08:40 (40 mins available)
        num_runs=1000,
    )
    assert sim["on_time_probability"] == 0.0
    assert sim["buffer_min"] < 0.0


def test_monte_carlo_near_mean_deadline():
    """Verify OTP is around 40-60% when deadline is equal to expected duration."""
    sim = run_monte_carlo_simulation(
        base_duration_min=60.0,
        variability_std_min=8.0,
        waiting_time_min=0.0,
        current_time_min=480,  # 08:00
        deadline_min=540,      # 09:00 (exactly 60 mins)
        num_runs=1000,
    )
    assert 40.0 <= sim["on_time_probability"] <= 60.0


def test_reliability_scoring_formula():
    """Verify formula: Score = buffer - (w1 * var) - (w2 * wait) - (w3 * trans)."""
    # w1=0.5, w2=0.3, w3=5.0
    buffer = 20.0
    variability = 8.0
    waiting = 10.0
    transfers = 1

    expected_score = 20.0 - (0.5 * 8.0) - (0.3 * 10.0) - (5.0 * 1)
    # 20 - 4 - 3 - 5 = 8.0
    score = calculate_reliability_score(
        buffer_min=buffer,
        variability_std_min=variability,
        waiting_time_min=waiting,
        transfers=transfers,
        w1=0.5,
        w2=0.3,
        w3=5.0,
    )
    assert score == pytest.approx(8.0, 0.01)

    # Increasing transfers should reduce score by w3 * delta
    score_2_transfers = calculate_reliability_score(
        buffer_min=buffer,
        variability_std_min=variability,
        waiting_time_min=waiting,
        transfers=2,
        w1=0.5,
        w2=0.3,
        w3=5.0,
    )
    assert score - score_2_transfers == pytest.approx(5.0, 0.01)


def test_evaluate_route_reliability_integration():
    """Verify full route evaluation pipeline with simulation and scoring."""
    dummy_route = {
        "route_id": "TEST_ROUTE",
        "route_name": "Test Express",
        "in_vehicle_time_min": 75.0,
        "waiting_time_min": 10.0,
        "delay_spread_min": 9.0,
        "transfers": 1,
    }

    evaluated = evaluate_route_reliability(
        dummy_route,
        current_time_str="08:00",
        deadline_str="10:00",
    )

    assert "on_time_probability" in evaluated
    assert "reliability_score" in evaluated
    assert "p90_arrival" in evaluated
    assert "confidence" in evaluated
    assert evaluated["confidence"] in ["High", "Moderate", "Low"]
