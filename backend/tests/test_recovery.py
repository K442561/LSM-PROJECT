"""Tests for recovery module, decision classification, and Latest Safe Departure."""

import pytest
from app.recovery import (
    compute_latest_safe_departure,
    generate_recovery_plan,
    attach_recommendation_reasons,
)


def test_compute_latest_safe_departure():
    """Verify LSD is deadline minus P90 duration."""
    deadline_min = 600  # 10:00
    p90_dur = 85.0      # 1 hour 25 mins

    lsd_min, lsd_str = compute_latest_safe_departure(deadline_min, p90_dur)
    assert lsd_min == 515  # 08:35
    assert lsd_str == "08:35"


def test_recovery_status_can_make_it():
    """Verify OTP >= 85% yields 'can_make_it'."""
    routes = [
        {
            "route_id": "R1",
            "route_name": "Route 1",
            "on_time_probability": 94.0,
            "p90_duration_min": 70.0,
            "buffer_min": 25.0,
            "summary_path": "A -> B",
        }
    ]
    recovery = generate_recovery_plan(routes, current_time_str="08:00", deadline_str="09:40")
    assert recovery["status"] == "can_make_it"
    assert "You can make it" in recovery["message"]
    assert recovery["minutes_until_lsd"] > 0


def test_recovery_status_risky():
    """Verify 50% <= OTP < 85% yields 'risky'."""
    routes = [
        {
            "route_id": "R1",
            "route_name": "Route 1",
            "on_time_probability": 68.0,
            "p90_duration_min": 85.0,
            "buffer_min": 8.0,
            "summary_path": "A -> B",
        }
    ]
    recovery = generate_recovery_plan(routes, current_time_str="08:00", deadline_str="09:30")
    assert recovery["status"] == "risky"
    assert "Risky" in recovery["message"]


def test_recovery_status_cannot():
    """Verify OTP < 50% yields 'cannot'."""
    routes = [
        {
            "route_id": "R1",
            "route_name": "Route 1",
            "on_time_probability": 15.0,
            "p90_duration_min": 110.0,
            "buffer_min": -20.0,
            "expected_arrival": "09:50",
            "summary_path": "A -> B",
        }
    ]
    recovery = generate_recovery_plan(routes, current_time_str="08:00", deadline_str="09:30")
    assert recovery["status"] == "cannot"
    assert "Cannot reach on time" in recovery["message"]
    assert "20 minutes late" in recovery["message"]


def test_attach_recommendation_reasons():
    """Verify ranking and highlighting the best route."""
    routes = [
        {
            "route_id": "R_LOW",
            "route_name": "Slow Train",
            "reliability_score": -15.0,
            "on_time_probability": 40.0,
            "buffer_min": -5.0,
            "delay_spread_min": 25.0,
        },
        {
            "route_id": "R_HIGH",
            "route_name": "Fast Bus",
            "reliability_score": 18.5,
            "on_time_probability": 92.0,
            "buffer_min": 22.0,
            "delay_spread_min": 8.0,
        },
    ]

    ranked = attach_recommendation_reasons(routes)
    assert len(ranked) == 2
    # R_HIGH should be first
    assert ranked[0]["route_id"] == "R_HIGH"
    assert ranked[0]["is_best"] is True
    assert "Recommended" in ranked[0]["recommendation_reason"]
    assert ranked[1]["is_best"] is False
