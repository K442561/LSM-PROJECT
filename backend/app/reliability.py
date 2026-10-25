"""Reliability and Monte Carlo Simulation Module for Mobility Recovery Engine.

Runs 1000 Monte Carlo simulation runs per route to calculate:
- On-Time Probability (percentage of runs arriving before the deadline)
- Expected arrival time
- 90th percentile arrival time (p90)
- Reliability score: buffer - (w1 * variability) - (w2 * waiting_time) - (w3 * transfers)
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Tuple
import numpy as np

from app.config import settings
from app.transit import parse_time_to_minutes, format_minutes_to_time

logger = logging.getLogger(__name__)


def run_monte_carlo_simulation(
    base_duration_min: float,
    variability_std_min: float,
    waiting_time_min: float,
    current_time_min: int,
    deadline_min: int,
    num_runs: int = settings.MONTE_CARLO_RUNS,
    legs: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute Monte Carlo simulation (1000 runs) to assess trip arrival variability.

    Arguments:
        base_duration_min: Mean in-vehicle travel time across the trip.
        variability_std_min: Total standard deviation / delay spread.
        waiting_time_min: Scheduled or expected initial wait time.
        current_time_min: Starting time in minutes from midnight.
        deadline_min: Target arrival deadline in minutes from midnight.
        num_runs: Iterations for simulation (default 1000).
        legs: Optional individual leg details to simulate multi-leg transfer risks.

    Returns:
        Dictionary with:
        - 'on_time_probability': float (0.0 to 100.0)
        - 'expected_duration_min': float
        - 'p90_duration_min': float (90th percentile travel duration)
        - 'expected_arrival_min': int
        - 'p90_arrival_min': int
        - 'buffer_min': float (deadline - expected_arrival)
    """
    rng = np.random.default_rng(seed=42)  # Fixed seed for reproducible benchmarks

    if legs and len(legs) > 1:
        # Simulate each leg independently to account for cascading transfer risks
        leg_simulations = []
        for leg in legs:
            leg_dur = float(leg.get("duration_min", 20.0))
            # Distribute variability proportionally to leg duration
            leg_std = max(1.0, variability_std_min * (leg_dur / max(1.0, base_duration_min)))
            # Truncated normal: leg travel time cannot drop below 40% of standard duration
            leg_samples = rng.normal(loc=leg_dur, scale=leg_std, size=num_runs)
            leg_samples = np.maximum(0.4 * leg_dur, leg_samples)
            leg_simulations.append(leg_samples)

        simulated_durations = np.sum(leg_simulations, axis=0)
    else:
        # Single distribution
        spread = max(1.0, variability_std_min)
        simulated_durations = rng.normal(loc=base_duration_min, scale=spread, size=num_runs)
        simulated_durations = np.maximum(0.4 * base_duration_min, simulated_durations)

    # Total trip time for each simulated run = waiting time + in-vehicle duration
    total_trip_times = waiting_time_min + simulated_durations
    arrival_times = current_time_min + total_trip_times

    # Compute statistics
    on_time_count = np.count_nonzero(arrival_times <= deadline_min)
    on_time_prob = float((on_time_count / num_runs) * 100.0)

    mean_duration = float(np.mean(total_trip_times))
    p90_duration = float(np.percentile(total_trip_times, 90.0))

    expected_arrival = int(round(current_time_min + mean_duration))
    p90_arrival = int(round(current_time_min + p90_duration))
    buffer_min = float(deadline_min - expected_arrival)

    return {
        "on_time_probability": round(on_time_prob, 1),
        "expected_duration_min": round(mean_duration, 1),
        "p90_duration_min": round(p90_duration, 1),
        "expected_arrival_min": expected_arrival,
        "p90_arrival_min": p90_arrival,
        "buffer_min": round(buffer_min, 1),
    }


def calculate_reliability_score(
    buffer_min: float,
    variability_std_min: float,
    waiting_time_min: float,
    transfers: int,
    w1: float = settings.WEIGHT_VARIABILITY,
    w2: float = settings.WEIGHT_WAITING,
    w3: float = settings.WEIGHT_TRANSFERS,
) -> float:
    """Calculate the overall reliability score for a route.

    Formula:
        Score = buffer - (w1 * variability) - (w2 * waiting_time) - (w3 * transfers)

    A higher score indicates a superior, lower-stress route that has adequate
    safety margin, lower risk of traffic jams, minimal wait time, and fewer transfers.
    """
    score = buffer_min - (w1 * variability_std_min) - (w2 * waiting_time_min) - (w3 * transfers)
    return round(float(score), 2)


def evaluate_route_reliability(
    route: Dict[str, Any],
    current_time_str: str,
    deadline_str: str,
) -> Dict[str, Any]:
    """Integrate Monte Carlo simulation and reliability scoring for a candidate route."""
    current_time_min = parse_time_to_minutes(current_time_str)
    deadline_min = parse_time_to_minutes(deadline_str)

    # Handle overnight deadline where deadline is past midnight (e.g. 23:30 -> 01:00)
    if deadline_min < current_time_min:
        deadline_min += 24 * 60

    base_duration = float(route.get("in_vehicle_time_min", route.get("duration_seconds", 3600) / 60.0))
    variability = float(route.get("delay_spread_min", 10.0))
    waiting = float(route.get("waiting_time_min", 0.0))
    transfers = int(route.get("transfers", 0))
    legs = route.get("legs", [])

    sim_results = run_monte_carlo_simulation(
        base_duration_min=base_duration,
        variability_std_min=variability,
        waiting_time_min=waiting,
        current_time_min=current_time_min,
        deadline_min=deadline_min,
        legs=legs,
    )

    score = calculate_reliability_score(
        buffer_min=sim_results["buffer_min"],
        variability_std_min=variability,
        waiting_time_min=waiting,
        transfers=transfers,
    )

    # Assess confidence based on variability and probabilities
    otp = sim_results["on_time_probability"]
    if variability <= 10.0 and otp >= 80.0:
        confidence = "High"
    elif variability <= 20.0 or otp >= 50.0:
        confidence = "Moderate"
    else:
        confidence = "Low"

    return {
        **route,
        "expected_departure": route.get("expected_departure", current_time_str),
        "expected_arrival": format_minutes_to_time(sim_results["expected_arrival_min"]),
        "p90_arrival": format_minutes_to_time(sim_results["p90_arrival_min"]),
        "p90_duration_min": sim_results["p90_duration_min"],
        "buffer_min": sim_results["buffer_min"],
        "on_time_probability": otp,
        "reliability_score": score,
        "confidence": confidence,
    }
