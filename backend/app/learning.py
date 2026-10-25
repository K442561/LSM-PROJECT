"""Learning Loop Module for Mobility Recovery Engine.

Processes actual user trip logs to update route and segment travel times
and variability using running statistical calibration.
"""

from __future__ import annotations
import logging
import math
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.models import TripLog, SegmentMetric
from app.transit import parse_time_to_minutes

logger = logging.getLogger(__name__)


def record_trip_and_update_metrics(
    db: Session,
    route_id: str,
    route_name: str,
    source: str,
    destination: str,
    actual_departure: str,
    actual_arrival: str,
    predicted_duration_min: float,
    actual_duration_min: Optional[float] = None,
    planned_departure: Optional[str] = None,
    planned_arrival: Optional[str] = None,
    notes: Optional[str] = None,
) -> TripLog:
    """Record a completed trip log and calibrate route statistics in the database."""
    # Compute actual duration from timestamps if not explicitly provided
    if actual_duration_min is None or actual_duration_min <= 0:
        dep_min = parse_time_to_minutes(actual_departure)
        arr_min = parse_time_to_minutes(actual_arrival)
        if arr_min < dep_min:
            arr_min += 24 * 60
        actual_duration_min = float(arr_min - dep_min)

    delay_min = round(float(actual_duration_min - predicted_duration_min), 1)

    # 1. Create TripLog record
    log_entry = TripLog(
        route_id=route_id,
        route_name=route_name,
        source=source,
        destination=destination,
        planned_departure=planned_departure,
        planned_arrival=planned_arrival,
        actual_departure=actual_departure,
        actual_arrival=actual_arrival,
        predicted_duration_min=round(float(predicted_duration_min), 1),
        actual_duration_min=round(float(actual_duration_min), 1),
        delay_min=delay_min,
        notes=notes,
    )
    db.add(log_entry)
    db.flush()

    # 2. Update SegmentMetric calibration for this route
    segment = db.query(SegmentMetric).filter(SegmentMetric.segment_id == route_id).first()

    if not segment:
        segment = SegmentMetric(
            segment_id=route_id,
            source_stop=source,
            dest_stop=destination,
            sample_count=1,
            mean_duration_min=actual_duration_min,
            std_dev_duration_min=max(2.0, abs(delay_min)),
            is_sample_data=False,
        )
        db.add(segment)
    else:
        old_count = segment.sample_count
        new_count = old_count + 1
        old_mean = segment.mean_duration_min
        old_std = segment.std_dev_duration_min

        # Welford's running update
        delta = actual_duration_min - old_mean
        new_mean = old_mean + (delta / new_count)
        delta2 = actual_duration_min - new_mean
        old_var = old_std ** 2
        new_var = ((old_count * old_var) + (delta * delta2)) / new_count
        new_std = math.sqrt(max(1.0, new_var))

        segment.sample_count = new_count
        segment.mean_duration_min = round(new_mean, 1)
        segment.std_dev_duration_min = round(new_std, 1)
        segment.is_sample_data = False  # Now calibrated with actual observations

    db.commit()
    db.refresh(log_entry)
    return log_entry
