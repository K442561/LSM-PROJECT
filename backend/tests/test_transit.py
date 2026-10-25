"""Tests for transit module time-dependent search and timetable validation."""

import pytest
from app.transit import (
    parse_time_to_minutes,
    format_minutes_to_time,
    load_timetables,
    find_next_departure,
    search_transit_routes,
)


def test_time_conversions():
    """Verify parsing and formatting 24-hour time strings."""
    assert parse_time_to_minutes("00:00") == 0
    assert parse_time_to_minutes("08:30") == 510
    assert parse_time_to_minutes("23:59") == 1439

    assert format_minutes_to_time(0) == "00:00"
    assert format_minutes_to_time(510) == "08:30"
    assert format_minutes_to_time(1440) == "00:00"

    with pytest.raises(ValueError):
        parse_time_to_minutes("invalid")

    with pytest.raises(ValueError):
        parse_time_to_minutes("25:00")


def test_timetables_json_loads_correctly():
    """Verify timetables.json is present and has required sample routes."""
    data = load_timetables()
    assert data is not None
    assert "routes" in data
    assert len(data["routes"]) >= 3

    route_ids = [r["route_id"] for r in data["routes"]]
    assert "ROUTE_BUS_NEW_BUS_STAND" in route_ids
    assert "ROUTE_BUS_ARANI" in route_ids
    assert "ROUTE_TRAIN_KATPADI" in route_ids


def test_find_next_departure():
    """Verify next scheduled departure lookup."""
    schedule = ["07:00", "08:30", "10:15", "14:00"]
    # Exactly on time
    assert find_next_departure(schedule, 510) == 510  # 08:30
    # Between departures: 09:00 -> 10:15 (615)
    assert find_next_departure(schedule, 540) == 615
    # Past last departure: 15:00 -> None
    assert find_next_departure(schedule, 900) is None


def test_transit_search_morning_query():
    """Verify search at 08:15 returns valid transit options with timings."""
    results = search_transit_routes("08:15")
    assert len(results) >= 3

    available_routes = [r for r in results if r["available"]]
    assert len(available_routes) >= 2  # Bus 1 and Bus 2 must be available

    # Check Route 1 (Bus via New Bus Stand)
    r1 = next(r for r in results if r["route_id"] == "ROUTE_BUS_NEW_BUS_STAND")
    assert r1["available"] is True
    assert r1["is_sample_data"] is True
    assert r1["transfers"] == 1
    # Expected departure should be after or at 08:15
    assert parse_time_to_minutes(r1["expected_departure"]) >= parse_time_to_minutes("08:15")
    # Arrival should be after departure
    assert parse_time_to_minutes(r1["expected_arrival"]) > parse_time_to_minutes(r1["expected_departure"])

    # Check Route 2 (Bus via Arani)
    r2 = next(r for r in results if r["route_id"] == "ROUTE_BUS_ARANI")
    assert r2["available"] is True
    assert r2["delay_spread_min"] < r1["delay_spread_min"]  # Arani has lower variability


def test_transit_search_late_night_returns_data_not_available():
    """Verify that querying at a time with no transit services returns 'data not available'. Never invents timings."""
    results = search_transit_routes("02:30")
    for r in results:
        # All night routes have no departures at 02:30
        assert r["available"] is False
        assert "data not available" in r["status_message"].lower()


def test_missing_timetable_file_returns_data_not_available():
    """Verify robust handling when timetable file path is nonexistent."""
    missing = search_transit_routes("08:00", timetables_data={"routes": []})
    assert missing == []
