"""SQLAlchemy data models for TripLog, LockedRoute, and SegmentMetric."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class TripLog(Base):
    """Stores actual user trips for the learning loop."""

    __tablename__ = "trip_logs"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String(50), index=True, nullable=False)
    route_name = Column(String(120), nullable=False)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    planned_departure = Column(String(50), nullable=True)
    planned_arrival = Column(String(50), nullable=True)
    actual_departure = Column(String(50), nullable=False)
    actual_arrival = Column(String(50), nullable=False)
    predicted_duration_min = Column(Float, nullable=False)
    actual_duration_min = Column(Float, nullable=False)
    delay_min = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class LockedRoute(Base):
    """Stores the active locked route to prevent accidental rerouting."""

    __tablename__ = "locked_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String(50), index=True, nullable=False)
    route_name = Column(String(120), nullable=False)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    deadline = Column(String(50), nullable=False)
    current_time = Column(String(50), nullable=False)
    expected_arrival = Column(String(50), nullable=False)
    on_time_probability = Column(Float, nullable=False)
    latest_safe_departure = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # can_make_it, risky, cannot
    recovery_message = Column(Text, nullable=True)
    route_data_json = Column(Text, nullable=False)  # JSON payload of route details
    is_active = Column(Boolean, default=True)
    locked_at = Column(DateTime, default=utc_now)


class SegmentMetric(Base):
    """Segment statistics (mean travel time and variability) for simulation."""

    __tablename__ = "segment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(String(100), unique=True, index=True, nullable=False)
    source_stop = Column(String(100), nullable=False)
    dest_stop = Column(String(100), nullable=False)
    sample_count = Column(Integer, default=1)
    mean_duration_min = Column(Float, nullable=False)
    std_dev_duration_min = Column(Float, nullable=False)
    is_sample_data = Column(Boolean, default=True)  # True if default sample data, False once updated by real logs
    last_updated = Column(DateTime, default=utc_now, onupdate=utc_now)

