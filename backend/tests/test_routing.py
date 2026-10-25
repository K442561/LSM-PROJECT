"""Tests for data models, A* pathfinding, and penalty-based alternative routing."""

import os
import pytest
import networkx as nx
from app.config import settings
from app.database import Base, engine
from app.models import TripLog, LockedRoute, SegmentMetric
from app.routing import (
    haversine_distance,
    haversine_time_heuristic,
    create_fallback_corridor_graph,
    load_or_fetch_road_graph,
    get_nearest_node,
    a_star_search,
    calculate_route_overlap,
    find_alternative_routes,
)


def test_database_models_initialization():
    """Verify that SQLAlchemy tables initialize and create properly in SQLite."""
    Base.metadata.create_all(bind=engine)
    # Check table names registered in metadata
    assert "trip_logs" in Base.metadata.tables
    assert "locked_routes" in Base.metadata.tables
    assert "segment_metrics" in Base.metadata.tables


def test_haversine_distance_between_vit_and_tiruvannamalai():
    """Verify Haversine formula against known coordinates.

    VIT Katpadi (~12.9692, 79.1559) to Tiruvannamalai (~12.2253, 79.0747).
    Expected straight-line distance is ~83 km (82,000 - 85,000 meters).
    """
    vit_lat, vit_lon = settings.VIT_COORDS
    tvm_lat, tvm_lon = settings.TVM_COORDS

    dist_meters = haversine_distance(vit_lat, vit_lon, tvm_lat, tvm_lon)
    dist_km = dist_meters / 1000.0

    assert 80.0 <= dist_km <= 86.0
    # Distance to self should be 0
    assert haversine_distance(vit_lat, vit_lon, vit_lat, vit_lon) == 0.0


def test_haversine_heuristic_admissibility():
    """Verify that heuristic never overestimates travel time."""
    G = create_fallback_corridor_graph()
    source = 101  # VIT Katpadi
    target = 115  # Tiruvannamalai Central Bus Stand

    h_time = haversine_time_heuristic(source, target, G, max_speed_kmh=80.0)
    assert h_time > 0.0

    # Solve actual A* path
    res = a_star_search(G, source, target)
    assert res is not None
    # Admissibility condition: h(n) <= actual_cost(n, target)
    assert h_time <= res["duration_seconds"]


def test_a_star_search_finds_path():
    """Verify A* search finds a valid path from VIT to Tiruvannamalai."""
    G = create_fallback_corridor_graph()
    source = 101
    target = 115

    result = a_star_search(G, source, target)
    assert result is not None
    path = result["path"]

    assert path[0] == source
    assert path[-1] == target
    assert len(path) >= 4  # Should pass through intermediate hubs
    assert result["distance_meters"] > 50000.0  # > 50 km
    assert result["duration_seconds"] > 3000.0  # > 50 minutes
    assert len(result["coordinates"]) == len(path)


def test_a_star_same_source_and_target():
    """Verify A* handles identical start and end gracefully."""
    G = create_fallback_corridor_graph()
    result = a_star_search(G, 101, 101)
    assert result is not None
    assert result["path"] == [101]
    assert result["distance_meters"] == 0.0
    assert result["duration_seconds"] == 0.0


def test_alternative_routes_penalty_method_and_overlap_filter():
    """Verify at least 3 distinct routes are generated with <= 80% overlap."""
    G = create_fallback_corridor_graph()
    source = 101  # VIT Katpadi
    target = 115  # Tiruvannamalai Bus Stand

    routes = find_alternative_routes(
        G,
        source=source,
        target=target,
        num_routes=3,
        max_overlap=0.80,
        penalty_multiplier=1.8,
    )

    assert len(routes) >= 3, f"Expected at least 3 routes, got {len(routes)}"

    # Check pairwise overlap
    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            overlap = calculate_route_overlap(routes[i]["path"], routes[j]["path"])
            assert overlap <= 0.80, f"Routes {i} and {j} overlap too much: {overlap:.2f} > 0.80"


def test_nearest_node_lookup():
    """Verify coordinate to nearest graph node lookup."""
    G = create_fallback_corridor_graph()
    # Query very close to VIT Katpadi
    node = get_nearest_node(G, lat=12.9690, lon=79.1555)
    assert node == 101
