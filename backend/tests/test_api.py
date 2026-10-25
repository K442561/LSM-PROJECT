"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure database schema is created before tests run."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    """Create test client instance."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Verify GET /health returns operational status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "cache_exists" in data
    assert "timestamp" in data


def test_plan_trip_endpoint_success(client):
    """Verify POST /plan produces ranked routes and recovery plan."""
    payload = {
        "source": "VIT Katpadi",
        "destination": "Tiruvannamalai",
        "current_time": "08:15",
        "deadline": "10:45",
    }
    resp = client.post("/plan", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["source"] == "VIT Katpadi"
    assert data["destination"] == "Tiruvannamalai"
    assert len(data["routes"]) >= 1

    # Verify best route properties
    best_route = data["routes"][0]
    assert best_route["is_best"] is True
    assert "on_time_probability" in best_route
    assert "reliability_score" in best_route
    assert "p90_arrival" in best_route
    assert "path_coordinates" in best_route
    assert len(best_route["path_coordinates"]) > 0

    # Verify recovery plan
    recovery = data["recovery"]
    assert recovery["status"] in ["can_make_it", "risky", "cannot"]
    assert "latest_safe_departure" in recovery
    assert "message" in recovery
    assert len(recovery["action_steps"]) > 0


def test_plan_trip_invalid_time_format(client):
    """Verify POST /plan rejects malformed time input with clear 400 error."""
    payload = {
        "source": "VIT Katpadi",
        "destination": "Tiruvannamalai",
        "current_time": "invalid_time",
        "deadline": "10:30",
    }
    resp = client.post("/plan", json=payload)
    assert resp.status_code == 400
    err = resp.json()
    assert "detail" in err or "error" in err


def test_route_lock_and_unlock_flow(client):
    """Verify POST /lock, GET /lock, and POST /unlock workflow."""
    lock_payload = {
        "route_id": "ROUTE_BUS_ARANI",
        "source": "VIT Katpadi",
        "destination": "Tiruvannamalai",
        "current_time": "08:30",
        "deadline": "10:45",
        "expected_arrival": "10:15",
        "on_time_probability": 92.5,
        "latest_safe_departure": "08:45",
        "status": "can_make_it",
        "recovery_message": "You can make it. Leave within 15 minutes.",
        "route_data": {
            "route_id": "ROUTE_BUS_ARANI",
            "route_name": "Route 2: Bus via VIT 11 Gate & Arani",
            "mode": "bus",
            "total_distance_km": 61.0,
            "on_time_probability": 92.5,
        },
    }

    # 1. Lock route
    post_resp = client.post("/lock", json=lock_payload)
    assert post_resp.status_code == 200
    lock_data = post_resp.json()
    assert lock_data["is_active"] is True
    assert lock_data["locked_id"] > 0

    # 2. Get locked route
    get_resp = client.get("/lock")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["is_active"] is True
    assert retrieved["route_id"] == "ROUTE_BUS_ARANI"
    assert retrieved["on_time_probability"] == 92.5

    # 3. Unlock route
    unlock_resp = client.post("/unlock")
    assert unlock_resp.status_code == 200
    assert unlock_resp.json()["is_active"] is False

    # 4. Verify no active locked route remains
    get_after = client.get("/lock")
    assert get_after.json()["is_active"] is False


def test_trip_logging_and_history_learning_loop(client):
    """Verify POST /log records trips, updates statistics, and GET /history aggregates data."""
    trip_payload = {
        "route_id": "ROUTE_BUS_ARANI",
        "route_name": "Route 2: Bus via VIT 11 Gate & Arani",
        "source": "VIT Katpadi",
        "destination": "Tiruvannamalai",
        "planned_departure": "08:45",
        "planned_arrival": "10:25",
        "actual_departure": "08:50",
        "actual_arrival": "10:35",
        "predicted_duration_min": 100.0,
        "actual_duration_min": 105.0,
        "notes": "Mild rain near Arani bypass.",
    }

    # 1. Post trip log
    log_resp = client.post("/log", json=trip_payload)
    assert log_resp.status_code == 200
    log_data = log_resp.json()
    assert log_data["route_id"] == "ROUTE_BUS_ARANI"
    assert log_data["actual_duration_min"] == 105.0
    assert log_data["delay_min"] == 5.0

    # 2. Query history
    hist_resp = client.get("/history")
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert history["total_trips"] >= 1
    assert any(log["route_id"] == "ROUTE_BUS_ARANI" for log in history["logs"])
