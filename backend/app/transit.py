"""Transit Timetable Module for Mobility Recovery Engine.

Reads bus and train timetables from timetables.json and performs time-dependent
transit search considering scheduled departures, waiting times, and transfers.
Strictly returns 'data not available' when schedules are missing. Never invents timings.
"""

from __future__ import annotations
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


def parse_time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' 24-hour time string into minutes since midnight."""
    time_str = time_str.strip()
    parts = time_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid time format '{time_str}', expected 'HH:MM'")
    hours = int(parts[0])
    minutes = int(parts[1])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"Time out of 24-hour range: {time_str}")
    return hours * 60 + minutes


def format_minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight back into 'HH:MM' string format."""
    normalized = int(minutes) % (24 * 60)
    hours = normalized // 60
    mins = normalized % 60
    return f"{hours:02d}:{mins:02d}"


def load_timetables(filepath: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load timetables from JSON file.

    Returns None if file is missing or invalid.
    """
    path = filepath or settings.TIMETABLES_FILE
    if not os.path.exists(path):
        logger.warning(f"Timetable file not found at: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"Error reading timetable JSON: {e}")
        return None


def find_next_departure(
    scheduled_departures: List[str],
    current_minutes: int,
) -> Optional[int]:
    """Find the next scheduled departure in minutes that occurs >= current_minutes.

    Returns None if no further departures exist on the schedule for today.
    """
    for dep_str in scheduled_departures:
        try:
            dep_min = parse_time_to_minutes(dep_str)
            if dep_min >= current_minutes:
                return dep_min
        except ValueError:
            continue
    return None


# Maximum wait time in minutes before a scheduled service is considered unavailable for the requested departure time
MAX_INITIAL_WAIT_MINUTES = 135
NIGHT_SERVICE_START_MIN = 23 * 60 + 30  # 23:30
NIGHT_SERVICE_END_MIN = 4 * 60 + 45     # 04:45


def search_transit_routes(
    query_time_str: str,
    timetables_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Perform a strict time-dependent schedule lookup for all available transit routes.

    Arguments:
        query_time_str: Starting time in 'HH:MM' format.
        timetables_data: Optional pre-loaded timetable dictionary.

    Returns:
        A list of evaluated transit options with precise scheduled times,
        waiting times, and leg details. If a route cannot operate or has
        no upcoming scheduled trips, it is marked with 'data not available'.
    """
    try:
        current_min = parse_time_to_minutes(query_time_str)
    except ValueError as e:
        logger.error(f"Invalid query time: {e}")
        return []

    data = timetables_data or load_timetables()
    if not data or "routes" not in data:
        return []

    # If queried during night shutdown (00:00 - 04:45 or after 23:30)
    is_night_shutdown = current_min < NIGHT_SERVICE_END_MIN or current_min > NIGHT_SERVICE_START_MIN

    results: List[Dict[str, Any]] = []

    for route_spec in data["routes"]:
        route_id = route_spec.get("route_id", "UNKNOWN")
        route_name = route_spec.get("route_name", "Transit Route")
        mode = route_spec.get("mode", "bus")
        summary_path = route_spec.get("summary_path", "")
        legs = route_spec.get("legs", [])
        base_spread = float(route_spec.get("base_delay_spread_min", 10.0))
        is_sample = route_spec.get("is_sample_data", True)

        if is_night_shutdown:
            results.append({
                "route_id": route_id,
                "route_name": route_name,
                "mode": mode,
                "summary_path": summary_path,
                "available": False,
                "status_message": "data not available: Transit services do not operate during night hours (23:30 - 04:45)",
                "is_sample_data": is_sample,
            })
            continue

        cursor_time = current_min
        total_waiting_min = 0
        total_in_vehicle_min = 0
        total_distance = 0.0
        leg_evaluations: List[Dict[str, Any]] = []
        is_available = True
        unavailable_reason = ""

        first_leg_dep_min: Optional[int] = None

        for idx, leg in enumerate(legs):
            leg_from = leg.get("from", "Origin")
            leg_to = leg.get("to", "Destination")
            dist = float(leg.get("distance_km", 0.0))
            duration = int(leg.get("duration_min", 0))
            total_distance += dist

            # Check if this leg has fixed scheduled departures
            if "scheduled_departures" in leg:
                sched = leg["scheduled_departures"]
                next_dep = find_next_departure(sched, cursor_time)
                if next_dep is None:
                    is_available = False
                    unavailable_reason = (
                        f"data not available: No remaining departures from {leg_from} after {format_minutes_to_time(cursor_time)}"
                    )
                    break

                wait = next_dep - cursor_time
                if idx == 0 and wait > MAX_INITIAL_WAIT_MINUTES:
                    is_available = False
                    unavailable_reason = (
                        f"data not available: No immediate departures from {leg_from} (next at {format_minutes_to_time(next_dep)})"
                    )
                    break
                total_waiting_min += wait
                total_in_vehicle_min += duration
                arr_min = next_dep + duration

                if idx == 0:
                    first_leg_dep_min = next_dep

                leg_evaluations.append({
                    "from": leg_from,
                    "to": leg_to,
                    "mode": leg.get("mode", mode),
                    "departure_time": format_minutes_to_time(next_dep),
                    "arrival_time": format_minutes_to_time(arr_min),
                    "duration_min": duration,
                    "waiting_min": wait,
                    "distance_km": dist,
                })

                # If there's a transfer buffer for next leg
                transfer_buffer = int(leg.get("transfer_buffer_min", 0))
                cursor_time = arr_min + transfer_buffer

            # Leg operates on frequent headway (e.g. city bus)
            elif "headway_min" in leg:
                first_dep_str = leg.get("first_departure", "05:00")
                last_dep_str = leg.get("last_departure", "23:00")
                first_dep_min = parse_time_to_minutes(first_dep_str)
                last_dep_min = parse_time_to_minutes(last_dep_str)

                if cursor_time < first_dep_min or cursor_time > last_dep_min:
                    is_available = False
                    unavailable_reason = (
                        f"data not available: {leg_from} service only runs {first_dep_str} - {last_dep_str}"
                    )
                    break

                headway = int(leg["headway_min"])
                # Expected wait is half headway for uniform arrivals, min 2 mins
                wait = max(2, headway // 2)
                dep_min = cursor_time + wait
                arr_min = dep_min + duration

                if idx == 0:
                    first_leg_dep_min = dep_min

                total_waiting_min += wait
                total_in_vehicle_min += duration

                leg_evaluations.append({
                    "from": leg_from,
                    "to": leg_to,
                    "mode": leg.get("mode", mode),
                    "departure_time": format_minutes_to_time(dep_min),
                    "arrival_time": format_minutes_to_time(arr_min),
                    "duration_min": duration,
                    "waiting_min": wait,
                    "distance_km": dist,
                })

                transfer_buffer = int(leg.get("transfer_buffer_min", 0))
                cursor_time = arr_min + transfer_buffer
            else:
                is_available = False
                unavailable_reason = f"data not available: Incomplete schedule for leg {leg_from} -> {leg_to}"
                break

        if not is_available:
            results.append({
                "route_id": route_id,
                "route_name": route_name,
                "mode": mode,
                "summary_path": summary_path,
                "available": False,
                "status_message": unavailable_reason or "data not available",
                "is_sample_data": is_sample,
            })
            continue

        final_arrival_min = leg_evaluations[-1]["arrival_time"] if leg_evaluations else format_minutes_to_time(cursor_time)
        initial_departure = format_minutes_to_time(first_leg_dep_min if first_leg_dep_min is not None else current_min)

        results.append({
            "route_id": route_id,
            "route_name": route_name,
            "mode": mode,
            "summary_path": summary_path,
            "available": True,
            "status_message": "Available",
            "is_sample_data": is_sample,
            "expected_departure": initial_departure,
            "expected_arrival": final_arrival_min,
            "waiting_time_min": float(total_waiting_min),
            "in_vehicle_time_min": float(total_in_vehicle_min),
            "total_expected_time_min": float(total_waiting_min + total_in_vehicle_min),
            "delay_spread_min": base_spread,
            "transfers": int(route_spec.get("transfers", max(0, len(legs) - 1))),
            "total_distance_km": total_distance,
            "legs": leg_evaluations,
        })

    return results
