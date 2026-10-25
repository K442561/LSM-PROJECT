"""FastAPI Application Entry Point for Mobility Recovery Engine.

Provides REST APIs for:
- POST /plan: Multi-route planning with reliability simulation and recovery guidance
- POST /lock & GET /lock: Active route lock management
- POST /log & GET /history: Trip logging and learning calibration loop
- GET /health: Health status and cache verification
"""

from __future__ import annotations
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.learning import record_trip_and_update_metrics
from app.models import LockedRoute, SegmentMetric, TripLog
from app.recovery import attach_recommendation_reasons, generate_recovery_plan
from app.reliability import evaluate_route_reliability
from app.geocoding import geocode_location, reverse_geocode
from app.routing import (
    a_star_search,
    create_fallback_corridor_graph,
    find_alternative_routes,
    get_nearest_node,
    get_pan_india_routes,
    load_or_fetch_road_graph,
)
from app.schemas import (
    Coordinate,
    GeocodeResult,
    HealthResponse,
    HistoryResponse,
    LockRequest,
    LockResponse,
    PlanRequest,
    PlanResponse,
    RouteOption,
    SegmentDetail,
    TripLogCreate,
    TripLogResponse,
)
from app.transit import (
    format_minutes_to_time,
    parse_time_to_minutes,
    search_transit_routes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Road graph in-memory instance
ROAD_GRAPH = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    global ROAD_GRAPH
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Loading road network graph...")
    try:
        ROAD_GRAPH = load_or_fetch_road_graph()
    except Exception as e:
        logger.warning(f"Error loading road graph ({e}), using fallback corridor graph.")
        ROAD_GRAPH = create_fallback_corridor_graph()

    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title="Mobility Recovery Engine API",
    description="Deadline-driven full-stack routing engine with Monte Carlo reliability simulation and recovery plans.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation and formatting errors with clear client messages."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid Input", "detail": str(exc)},
    )


@app.get("/health", response_model=HealthResponse, tags=["System"])
def get_health(db: Session = Depends(get_db)):
    """Check backend operational health and cache availability."""
    import os
    has_active_lock = db.query(LockedRoute).filter(LockedRoute.is_active == True).first() is not None
    cache_exists = os.path.exists(settings.GRAPH_CACHE_FILE)
    return HealthResponse(
        status="healthy",
        app=settings.APP_NAME,
        cache_exists=cache_exists,
        active_locked_route=has_active_lock,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/geocode", tags=["Geocoding"])
def geocode_query(q: str):
    """Geocode any location or landmark across India."""
    lat, lon, display = geocode_location(q)
    return {"query": q, "lat": lat, "lon": lon, "display_name": display}


@app.post("/plan", response_model=PlanResponse, tags=["Routing"])
def plan_trip(req: PlanRequest, db: Session = Depends(get_db)):
    """Generate and rank deadline-aware routes with reliability simulations and recovery plan.

    Supports ANY origin and destination across India entered manually or picked on map.
    Calculates shortest route and distinct alternatives for Car/Cab, Bus, Train, or All Modes.
    """
    global ROAD_GRAPH
    if ROAD_GRAPH is None:
        ROAD_GRAPH = load_or_fetch_road_graph()

    # Validate time formats
    try:
        cur_min = parse_time_to_minutes(req.current_time)
        dead_min = parse_time_to_minutes(req.deadline)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Resolve Coordinates for Source & Destination across India
    if req.source_coords:
        s_lat = req.source_coords.lat
        s_lon = req.source_coords.lon
        s_name = reverse_geocode(s_lat, s_lon)
    else:
        s_lat, s_lon, s_name = geocode_location(req.source)

    if req.dest_coords:
        d_lat = req.dest_coords.lat
        d_lon = req.dest_coords.lon
        d_name = reverse_geocode(d_lat, d_lon)
    else:
        d_lat, d_lon, d_name = geocode_location(req.destination)

    # Dynamic Pan-India Routing for any input across India
    # Generates Shortest Route and at least 3 distinct alternative corridors
    pan_routes = get_pan_india_routes(
        origin_lat=s_lat,
        origin_lon=s_lon,
        dest_lat=d_lat,
        dest_lon=d_lon,
        selected_mode=req.mode,
        origin_name=s_name,
        dest_name=d_name,
    )

    evaluated_routes: List[Dict[str, Any]] = []
    for r in pan_routes:
        route_id = r["route_id"]
        # Check if database has calibrated historical metrics for this corridor
        calibrated = db.query(SegmentMetric).filter(SegmentMetric.segment_id == route_id).first()
        if calibrated:
            r["delay_spread_min"] = calibrated.std_dev_duration_min

        evaluated = evaluate_route_reliability(
            r, current_time_str=req.current_time, deadline_str=req.deadline
        )
        evaluated_routes.append(evaluated)

    # Rank routes primarily by reliability score and OTP
    ranked_routes = attach_recommendation_reasons(evaluated_routes)

    # Formulate recovery plan and countdown to Latest Safe Departure (LSD)
    recovery_plan = generate_recovery_plan(
        ranked_routes,
        current_time_str=req.current_time,
        deadline_str=req.deadline,
    )

    # Build response schemas
    formatted_routes: List[RouteOption] = []
    for r in ranked_routes:
        segments: List[SegmentDetail] = []
        for leg in r.get("legs", []):
            segments.append(
                SegmentDetail(
                    segment_id=f"{leg.get('from')}_TO_{leg.get('to')}".replace(" ", "_")[:60],
                    from_stop=leg.get("from", s_name),
                    to_stop=leg.get("to", d_name),
                    mode=leg.get("mode", r["mode"]),
                    distance_km=float(leg.get("distance_km", r.get("total_distance_km", 0.0))),
                    expected_time_min=float(leg.get("duration_min", r.get("in_vehicle_time_min", 0.0))),
                    delay_spread_min=round(float(r.get("delay_spread_min", 8.0)) / max(1, len(r.get("legs", []))), 1),
                    is_sample_data=r.get("is_sample_data", False),
                )
            )

        formatted_routes.append(
            RouteOption(
                route_id=r["route_id"],
                route_name=r["route_name"],
                mode=r["mode"],
                summary_path=r.get("summary_path", ""),
                total_distance_km=float(r.get("total_distance_km", 0.0)),
                waiting_time_min=float(r.get("waiting_time_min", 0.0)),
                in_vehicle_time_min=float(r.get("in_vehicle_time_min", 0.0)),
                total_expected_time_min=float(r.get("total_expected_time_min", 0.0)),
                delay_spread_min=float(r.get("delay_spread_min", 0.0)),
                transfers=int(r.get("transfers", 0)),
                expected_departure=r.get("expected_departure", req.current_time),
                expected_arrival=r.get("expected_arrival", ""),
                p90_arrival=r.get("p90_arrival", ""),
                buffer_min=float(r.get("buffer_min", 0.0)),
                on_time_probability=float(r.get("on_time_probability", 0.0)),
                reliability_score=float(r.get("reliability_score", 0.0)),
                confidence=r.get("confidence", "Moderate"),
                is_best=r.get("is_best", False),
                recommendation_reason=r.get("recommendation_reason", ""),
                segments=segments,
                path_coordinates=r.get("path_coordinates", []),
            )
        )

    return PlanResponse(
        source=req.source,
        destination=req.destination,
        source_display=s_name,
        destination_display=d_name,
        source_coords=Coordinate(lat=s_lat, lon=s_lon),
        dest_coords=Coordinate(lat=d_lat, lon=d_lon),
        current_time=req.current_time,
        deadline=req.deadline,
        selected_mode=req.mode,
        routes=formatted_routes,
        recovery=recovery_plan,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/lock", response_model=LockResponse, tags=["Route Lock"])
def lock_route(req: LockRequest, db: Session = Depends(get_db)):
    """Lock a selected route to protect against accidental changes."""
    # Deactivate existing locks
    db.query(LockedRoute).filter(LockedRoute.is_active == True).update({"is_active": False})

    new_lock = LockedRoute(
        route_id=req.route_id,
        route_name=req.route_data.get("route_name", "Locked Route"),
        source=req.source,
        destination=req.destination,
        deadline=req.deadline,
        current_time=req.current_time,
        expected_arrival=req.expected_arrival,
        on_time_probability=req.on_time_probability,
        latest_safe_departure=req.latest_safe_departure,
        status=req.status,
        recovery_message=req.recovery_message,
        route_data_json=json.dumps(req.route_data),
        is_active=True,
    )
    db.add(new_lock)
    db.commit()
    db.refresh(new_lock)

    return LockResponse(
        message=f"Route '{new_lock.route_name}' successfully locked.",
        locked_id=new_lock.id,
        is_active=True,
        locked_at=new_lock.locked_at.isoformat(),
        route_data=json.loads(new_lock.route_data_json),
    )


@app.get("/lock", tags=["Route Lock"])
def get_locked_route(db: Session = Depends(get_db)):
    """Retrieve the currently active locked route."""
    locked = db.query(LockedRoute).filter(LockedRoute.is_active == True).order_by(LockedRoute.id.desc()).first()
    if not locked:
        return {"is_active": False, "locked_route": None}

    return {
        "is_active": True,
        "locked_id": locked.id,
        "route_id": locked.route_id,
        "route_name": locked.route_name,
        "source": locked.source,
        "destination": locked.destination,
        "deadline": locked.deadline,
        "current_time": locked.current_time,
        "expected_arrival": locked.expected_arrival,
        "on_time_probability": locked.on_time_probability,
        "latest_safe_departure": locked.latest_safe_departure,
        "status": locked.status,
        "recovery_message": locked.recovery_message,
        "route_data": json.loads(locked.route_data_json),
        "locked_at": locked.locked_at.isoformat(),
    }


@app.post("/unlock", tags=["Route Lock"])
def unlock_active_route(db: Session = Depends(get_db)):
    """Unlock and clear active locked route after user confirmation."""
    db.query(LockedRoute).filter(LockedRoute.is_active == True).update({"is_active": False})
    db.commit()
    return {"message": "Route unlocked successfully.", "is_active": False}


@app.post("/log", response_model=TripLogResponse, tags=["Learning Loop"])
def log_actual_trip(req: TripLogCreate, db: Session = Depends(get_db)):
    """Log actual trip departure and arrival times to calibrate segment models."""
    log_entry = record_trip_and_update_metrics(
        db=db,
        route_id=req.route_id,
        route_name=req.route_name,
        source=req.source,
        destination=req.destination,
        actual_departure=req.actual_departure,
        actual_arrival=req.actual_arrival,
        predicted_duration_min=req.predicted_duration_min,
        actual_duration_min=req.actual_duration_min,
        planned_departure=req.planned_departure,
        planned_arrival=req.planned_arrival,
        notes=req.notes,
    )

    return TripLogResponse(
        id=log_entry.id,
        route_id=log_entry.route_id,
        route_name=log_entry.route_name,
        source=log_entry.source,
        destination=log_entry.destination,
        planned_departure=log_entry.planned_departure,
        planned_arrival=log_entry.planned_arrival,
        actual_departure=log_entry.actual_departure,
        actual_arrival=log_entry.actual_arrival,
        predicted_duration_min=log_entry.predicted_duration_min,
        actual_duration_min=log_entry.actual_duration_min,
        delay_min=log_entry.delay_min,
        notes=log_entry.notes,
        created_at=log_entry.created_at.isoformat(),
    )


@app.get("/history", response_model=HistoryResponse, tags=["Learning Loop"])
def get_trip_history(db: Session = Depends(get_db)):
    """Retrieve historical logs with predicted vs actual durations."""
    logs = db.query(TripLog).order_by(TripLog.id.desc()).all()
    formatted = [
        TripLogResponse(
            id=log.id,
            route_id=log.route_id,
            route_name=log.route_name,
            source=log.source,
            destination=log.destination,
            planned_departure=log.planned_departure,
            planned_arrival=log.planned_arrival,
            actual_departure=log.actual_departure,
            actual_arrival=log.actual_arrival,
            predicted_duration_min=log.predicted_duration_min,
            actual_duration_min=log.actual_duration_min,
            delay_min=log.delay_min,
            notes=log.notes,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]

    avg_delay = 0.0
    if logs:
        avg_delay = round(float(sum(l.delay_min for l in logs) / len(logs)), 1)

    return HistoryResponse(
        total_trips=len(logs),
        average_delay_min=avg_delay,
        logs=formatted,
    )


# -------------------------------------------------------------------------
# Static Frontend Single-Port Serving (Unified Production & Network Mode)
# -------------------------------------------------------------------------
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Serve exact file if it exists, otherwise fallback to React index.html
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")

