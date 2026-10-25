"""Recovery and Decision Logic Module for Mobility Recovery Engine.

Evaluates on-time probability against deadlines to determine trip status:
- 'can_make_it' (OTP >= 85%)
- 'risky' (50% <= OTP < 85%)
- 'cannot' (OTP < 50%)
Calculates Latest Safe Departure (LSD) time and provides recovery plans if a bus is missed.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.transit import parse_time_to_minutes, format_minutes_to_time

logger = logging.getLogger(__name__)


def compute_latest_safe_departure(
    deadline_min: int,
    p90_duration_min: float,
) -> Tuple[int, str]:
    """Compute Latest Safe Departure (LSD) in minutes and 'HH:MM' string.

    LSD = Deadline - P90 Travel Duration.
    Departing before or at LSD guarantees >= 90% statistical confidence
    of reaching the destination before the deadline.
    """
    lsd_min = int(round(deadline_min - p90_duration_min))
    return lsd_min, format_minutes_to_time(lsd_min)


def generate_recovery_plan(
    ranked_routes: List[Dict[str, Any]],
    current_time_str: str,
    deadline_str: str,
) -> Dict[str, Any]:
    """Analyze ranked routes and produce decision guidance, countdown, and contingency.

    Arguments:
        ranked_routes: Routes sorted with the recommended route first.
        current_time_str: Trip start time in 'HH:MM'.
        deadline_str: Target arrival deadline in 'HH:MM'.

    Returns:
        Dictionary containing:
        - 'status': "can_make_it", "risky", or "cannot"
        - 'message': User-facing summary alert
        - 'latest_safe_departure': "HH:MM"
        - 'minutes_until_lsd': float minutes remaining to safely depart
        - 'missed_transit_fallback': Contingency option if primary departure is missed
        - 'action_steps': List of concrete guidance steps
    """
    current_min = parse_time_to_minutes(current_time_str)
    deadline_min = parse_time_to_minutes(deadline_str)
    if deadline_min < current_min:
        deadline_min += 24 * 60

    if not ranked_routes:
        return {
            "status": "cannot",
            "message": "Cannot reach on time. No transit or road routes available for this time.",
            "latest_safe_departure": current_time_str,
            "minutes_until_lsd": 0.0,
            "missed_transit_fallback": "Wait for morning schedule or book private transport.",
            "action_steps": ["Check alternative travel times during active operational hours."],
        }

    best_route = ranked_routes[0]
    best_otp = float(best_route.get("on_time_probability", 0.0))
    p90_dur = float(best_route.get("p90_duration_min", 90.0))
    buffer_min = float(best_route.get("buffer_min", 0.0))

    lsd_min, lsd_str = compute_latest_safe_departure(deadline_min, p90_dur)
    minutes_until_lsd = round(float(lsd_min - current_min), 1)

    # Secondary / backup route for contingency
    contingency_fallback = None
    if len(ranked_routes) > 1:
        alt_route = ranked_routes[1]
        contingency_fallback = (
            f"If {best_route.get('route_name', 'primary route')} is delayed or missed: "
            f"Take {alt_route.get('route_name', 'Alternative')} via {alt_route.get('summary_path', 'backup corridor')} "
            f"(Arrives ~{alt_route.get('expected_arrival', 'N/A')}, OTP: {alt_route.get('on_time_probability', 0)}%)."
        )
    else:
        contingency_fallback = "Take a direct taxi or auto-rickshaw via Arani bypass if bus is missed."

    # Status determination
    if best_otp >= 85.0:
        status = "can_make_it"
        if minutes_until_lsd > 0:
            message = f"You can make it. Leave within {int(minutes_until_lsd)} minutes ({lsd_str}) via {best_route.get('route_name')}."
        else:
            message = f"You can make it, but leave immediately ({lsd_str} was recommended departure)!"

        action_steps = [
            f"Depart by {lsd_str} to preserve safety buffer ({int(buffer_min)} mins remaining).",
            f"Proceed to {best_route.get('summary_path', 'departure point')}.",
            "Lock this route to monitor live deadline updates."
        ]

    elif best_otp >= 50.0:
        status = "risky"
        # Check if alternative has lower delay spread
        rec_name = best_route.get("route_name", "primary route")
        if len(ranked_routes) > 1 and ranked_routes[1].get("delay_spread_min", 99) < best_route.get("delay_spread_min", 10):
            better_spread_route = ranked_routes[1]
            message = (
                f"Risky. Take {better_spread_route.get('route_name')} to bypass traffic. "
                f"Expected arrival: {better_spread_route.get('expected_arrival')}."
            )
        else:
            message = f"Risky route with tight buffer ({int(buffer_min)} mins). Leave immediately by {lsd_str}."

        action_steps = [
            f"Tight margin: Latest safe departure is {lsd_str} ({int(max(0, minutes_until_lsd))}m left).",
            "Avoid stops and proceed directly to boarding gate.",
            f"Backup plan: {contingency_fallback}"
        ]

    else:
        status = "cannot"
        late_by_min = abs(int(buffer_min))
        message = f"Cannot reach on time. Best option arrives {late_by_min} minutes late."

        action_steps = [
            f"Deadline ({deadline_str}) cannot be met using standard schedules.",
            f"Best available arrival is {best_route.get('expected_arrival')} (~{late_by_min} mins past deadline).",
            f"Recovery option: Consider private express taxi or notifying host of expected arrival at {best_route.get('expected_arrival')}."
        ]

    return {
        "status": status,
        "message": message,
        "latest_safe_departure": lsd_str,
        "minutes_until_lsd": minutes_until_lsd,
        "missed_transit_fallback": contingency_fallback,
        "action_steps": action_steps,
    }


def attach_recommendation_reasons(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Highlight the best route with a clear one-line rationale."""
    if not routes:
        return []

    # Sort routes primarily by reliability score descending, then on_time_probability descending
    sorted_routes = sorted(
        routes,
        key=lambda r: (r.get("reliability_score", -999.0), r.get("on_time_probability", 0.0)),
        reverse=True,
    )

    for idx, r in enumerate(sorted_routes):
        if idx == 0:
            r["is_best"] = True
            otp = r.get("on_time_probability", 0.0)
            buf = int(r.get("buffer_min", 0.0))
            spread = r.get("delay_spread_min", 10.0)
            r["recommendation_reason"] = (
                f"Recommended: Highest reliability ({otp}% on-time probability) with {buf}m safety buffer "
                f"and low variability (±{spread:.0f}m)."
            )
        else:
            r["is_best"] = False
            r["recommendation_reason"] = f"Alternative option with {r.get('on_time_probability', 0)}% on-time probability."

    return sorted_routes
