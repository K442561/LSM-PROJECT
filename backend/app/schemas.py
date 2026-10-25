"""Pydantic schemas for request and response validation."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    """Geographic coordinate representation."""
    lat: float
    lon: float


class SegmentDetail(BaseModel):
    """Detailed view of a single route segment."""
    segment_id: str
    from_stop: str
    to_stop: str
    mode: str = "bus"  # "bus", "train", "walk", "auto"
    distance_km: float
    expected_time_min: float
    delay_spread_min: float
    is_sample_data: bool = True


class RouteOption(BaseModel):
    """Evaluated route alternative with reliability metrics."""
    route_id: str
    route_name: str
    mode: str  # "bus", "train", "mixed"
    summary_path: str
    total_distance_km: float
    waiting_time_min: float
    in_vehicle_time_min: float
    total_expected_time_min: float
    delay_spread_min: float
    transfers: int
    expected_departure: str
    expected_arrival: str
    p90_arrival: str
    buffer_min: float
    on_time_probability: float  # 0 to 100%
    reliability_score: float
    confidence: str  # "High", "Moderate", "Low"
    is_best: bool = False
    recommendation_reason: str = ""
    segments: list[SegmentDetail] = []
    path_coordinates: list[list[float]] = []  # [[lat, lon], ...]


class RecoveryPlan(BaseModel):
    """Contingency and decision guidance."""
    status: str  # "can_make_it", "risky", "cannot"
    message: str
    latest_safe_departure: str
    minutes_until_lsd: float
    missed_transit_fallback: Optional[str] = None
    action_steps: list[str] = []


class GeocodeResult(BaseModel):
    """Result from location geocoding."""
    display_name: str
    lat: float
    lon: float


class PlanRequest(BaseModel):
    """Request payload for route planning."""
    source: str = Field(default="VIT Katpadi", description="Starting landmark or address")
    destination: str = Field(default="Tiruvannamalai", description="Ending landmark or address")
    current_time: str = Field(description="Trip start time in HH:MM format (24-hour)")
    deadline: str = Field(description="Strict arrival deadline in HH:MM format (24-hour)")
    mode: str = Field(default="all", description="Transport mode: all, driving, bus, train")
    source_coords: Optional[Coordinate] = None
    dest_coords: Optional[Coordinate] = None


class PlanResponse(BaseModel):
    """Complete response returned by POST /plan."""
    source: str
    destination: str
    source_display: Optional[str] = None
    destination_display: Optional[str] = None
    source_coords: Optional[Coordinate] = None
    dest_coords: Optional[Coordinate] = None
    current_time: str
    deadline: str
    selected_mode: str = "all"
    routes: list[RouteOption]
    recovery: RecoveryPlan
    generated_at: str


class LockRequest(BaseModel):
    """Request payload to lock a route."""
    route_id: str
    source: str
    destination: str
    current_time: str
    deadline: str
    expected_arrival: str
    on_time_probability: float
    latest_safe_departure: str
    status: str
    recovery_message: Optional[str] = None
    route_data: dict[str, Any]


class LockResponse(BaseModel):
    """Response when a route is locked."""
    message: str
    locked_id: int
    is_active: bool
    locked_at: str
    route_data: dict[str, Any]


class TripLogCreate(BaseModel):
    """Request payload to record an actual trip."""
    route_id: str
    route_name: str
    source: str
    destination: str
    planned_departure: Optional[str] = None
    planned_arrival: Optional[str] = None
    actual_departure: str
    actual_arrival: str
    predicted_duration_min: float
    actual_duration_min: float
    notes: Optional[str] = None


class TripLogResponse(BaseModel):
    """Schema for returning logged trips."""
    id: int
    route_id: str
    route_name: str
    source: str
    destination: str
    planned_departure: Optional[str]
    planned_arrival: Optional[str]
    actual_departure: str
    actual_arrival: str
    predicted_duration_min: float
    actual_duration_min: float
    delay_min: float
    notes: Optional[str]
    created_at: str


class HistoryResponse(BaseModel):
    """Comparison history of predicted vs actual trips."""
    total_trips: int
    average_delay_min: float
    logs: list[TripLogResponse]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app: str
    cache_exists: bool
    active_locked_route: bool
    timestamp: str
