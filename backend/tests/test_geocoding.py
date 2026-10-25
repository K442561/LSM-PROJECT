"""Tests for Pan-India geocoding, reverse geocoding, and dynamic route routing."""

import pytest
from app.geocoding import geocode_location, reverse_geocode, match_offline_database
from app.routing import get_pan_india_routes


def test_offline_geocoding_major_cities():
    """Verify offline dictionary resolution for major Indian cities and campuses."""
    vit_lat, vit_lon, vit_desc = geocode_location("VIT Katpadi")
    assert pytest.approx(vit_lat, 0.01) == 12.9692
    assert pytest.approx(vit_lon, 0.01) == 79.1559
    assert "VIT" in vit_desc or "Vellore" in vit_desc

    blr_lat, blr_lon, blr_desc = geocode_location("Bengaluru")
    assert pytest.approx(blr_lat, 0.05) == 12.9716
    assert pytest.approx(blr_lon, 0.05) == 77.5946

    mum_lat, mum_lon, _ = geocode_location("Mumbai")
    assert pytest.approx(mum_lat, 0.05) == 19.0760
    assert pytest.approx(mum_lon, 0.05) == 72.8777

    del_lat, del_lon, _ = geocode_location("Delhi")
    assert pytest.approx(del_lat, 0.05) == 28.6139
    assert pytest.approx(del_lon, 0.05) == 77.2090


def test_reverse_geocoding():
    """Verify reverse geocoding from coordinates to human-readable Indian location."""
    name = reverse_geocode(12.9692, 79.1559)
    assert "VIT" in name or "Vellore" in name

    chn_name = reverse_geocode(13.0827, 80.2707)
    assert "Chennai" in chn_name


def test_pan_india_routes_generation():
    """Verify dynamic route calculation between two arbitrary Indian cities (Chennai to Bengaluru)."""
    # Chennai (13.0827, 80.2707) to Bengaluru (12.9716, 77.5946)
    routes = get_pan_india_routes(
        origin_lat=13.0827,
        origin_lon=80.2707,
        dest_lat=12.9716,
        dest_lon=77.5946,
        selected_mode="all",
        origin_name="Chennai Central",
        dest_name="Bengaluru Majestic",
    )

    assert len(routes) >= 3
    # Check that route 1 (shortest/driving) has realistic distance ~300-360 km
    r1 = routes[0]
    assert 280.0 <= r1["total_distance_km"] <= 380.0
    assert len(r1["path_coordinates"]) >= 2

    # Check mode diversity when mode="all"
    modes = [r["mode"] for r in routes]
    assert "car" in modes
    assert "bus" in modes
    assert "train" in modes


def test_pan_india_mode_specific_filtering():
    """Verify driving vs train mode configurations."""
    driving_routes = get_pan_india_routes(
        origin_lat=18.5204,
        origin_lon=73.8567,
        dest_lat=19.0760,
        dest_lon=72.8777,
        selected_mode="driving",
        origin_name="Pune",
        dest_name="Mumbai",
    )
    for r in driving_routes:
        assert r["mode"] == "car"
        assert r["waiting_time_min"] < 10.0  # minimal waiting time for car

    train_routes = get_pan_india_routes(
        origin_lat=18.5204,
        origin_lon=73.8567,
        dest_lat=19.0760,
        dest_lon=72.8777,
        selected_mode="train",
        origin_name="Pune",
        dest_name="Mumbai",
    )
    for r in train_routes:
        assert r["mode"] == "train"
        assert r["waiting_time_min"] >= 20.0  # railway station wait buffer
