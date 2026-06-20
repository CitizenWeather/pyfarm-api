"""Tests for pyfarm-api."""

import pytest
from fastapi.testclient import TestClient

from pyfarm.api import create_app
from pyfarm.api.client import ControlClient


@pytest.fixture
def mock_control_client():
    """Create mock control client."""
    class MockControlClient(ControlClient):
        async def get_status(self):
            return {
                "run_id": "test-run",
                "spec_name": "test-spec",
                "current_stage": "V2",
                "elapsed_days": 5.5,
                "readings": {"temperature": {"value": 23.5, "unit": "°C"}},
                "derived": {"vpd": 1.2},
                "actuator_states": {"led_1": {"state": True}},
                "recent_events": [],
            }

        async def get_history(self, sensor_id=None, metric=None, limit=100):
            return {
                "readings": [],
                "count": 0,
            }

        async def get_events(self, limit=50):
            return {"events": [], "count": 0}

        async def health(self):
            return {"status": "ok"}

    return MockControlClient("http://localhost:8000")


@pytest.fixture
def client(mock_control_client):
    """Create test client."""
    app = create_app(control_client=mock_control_client)
    return TestClient(app)


def test_health(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_status_requires_auth(client):
    """Test that status endpoint requires authentication."""
    response = client.get("/api/v1/status")
    # Missing credentials -> 401 Unauthorized (HTTPBearer is configured with
    # auto_error=False and the dependency raises 401 explicitly).
    assert response.status_code == 401


def test_status_with_invalid_token(client):
    """Test status with invalid token."""
    response = client.get(
        "/api/v1/status",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


# Note: Full integration tests would require:
# - Running pyfarm-auth and pyfarm-control services
# - Getting valid JWT tokens
# - Testing end-to-end flows
#
# These are covered by integration test suite in deployment testing
