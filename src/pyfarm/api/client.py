"""Client for communicating with pyfarm-control."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx


class ControlClient:
    """HTTP client for pyfarm-control."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize control client.

        Args:
            base_url: Base URL of pyfarm-control service.
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def get_status(self) -> dict[str, Any]:
        """Get current control status.

        Returns:
            Control context snapshot.
        """
        response = await self.client.get("/api/v1/status")
        response.raise_for_status()
        return response.json()

    async def get_history(
        self,
        sensor_id: str | None = None,
        metric: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get historical readings.

        Args:
            sensor_id: Filter by sensor ID.
            metric: Filter by metric name.
            limit: Maximum readings to return.

        Returns:
            Historical readings response.
        """
        params = {"limit": limit}
        if sensor_id:
            params["sensor_id"] = sensor_id
        if metric:
            params["metric"] = metric

        response = await self.client.get("/api/v1/history", params=params)
        response.raise_for_status()
        return response.json()

    async def get_events(self, limit: int = 50) -> dict[str, Any]:
        """Get recent events.

        Args:
            limit: Maximum events to return.

        Returns:
            Events response.
        """
        response = await self.client.get("/api/v1/events", params={"limit": limit})
        response.raise_for_status()
        return response.json()

    async def override_actuator(self, actuator_id: str, state: bool) -> dict[str, Any]:
        """Override an actuator.

        Args:
            actuator_id: ID of actuator to override.
            state: Desired state (True=on, False=off).

        Returns:
            Override response.
        """
        response = await self.client.post(
            "/api/v1/override",
            params={"actuator_id": actuator_id, "state": state},
        )
        response.raise_for_status()
        return response.json()

    async def health(self) -> dict[str, str]:
        """Check control service health.

        Returns:
            Health check response.
        """
        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, Exception):
            return {"status": "unavailable"}

    async def close(self) -> None:
        """Close HTTP session."""
        await self.client.aclose()


def get_control_client() -> ControlClient:
    """Get configured control client.

    Uses CONTROL_URL env var (default: http://localhost:8000).
    """
    control_url = os.getenv("CONTROL_URL", "http://localhost:8000")
    return ControlClient(control_url)
