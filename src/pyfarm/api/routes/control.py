"""Control engine routes."""

from __future__ import annotations

from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..client import ControlClient
from ..models import (
    ControlStatusResponse,
    EventLogResponse,
    EventResponse,
    HistoryResponse,
    SensorReadingResponse,
)


def create_router(
    control_client: ControlClient,
    get_current_user: Callable,
) -> APIRouter:
    """Create control routes with dependencies.

    Args:
        control_client: Control service client.
        get_current_user: Dependency to get current authenticated user.
    """
    router = APIRouter()

    @router.get("/status", response_model=ControlStatusResponse)
    async def get_status(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        """Get current control context status.

        Requires: Any authenticated user.
        """
        try:
            return await control_client.get_status()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Control service unavailable: {e}",
            )

    @router.get("/history", response_model=HistoryResponse)
    async def get_history(
        sensor_id: str | None = Query(None),
        metric: str | None = Query(None),
        limit: int = Query(100, ge=1, le=10000),
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        """Get historical sensor readings.

        Query parameters:
        - sensor_id: Filter by sensor ID
        - metric: Filter by metric name
        - limit: Maximum readings to return (default: 100, max: 10000)

        Requires: Any authenticated user.
        """
        try:
            data = await control_client.get_history(
                sensor_id=sensor_id,
                metric=metric,
                limit=limit,
            )
            return HistoryResponse(
                readings=[SensorReadingResponse(**r) for r in data.get("readings", [])],
                count=data.get("count", 0),
                sensor_id=sensor_id,
                metric=metric,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Control service unavailable: {e}",
            )

    @router.get("/events", response_model=EventLogResponse)
    async def get_events(
        limit: int = Query(50, ge=1, le=1000),
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        """Get recent control events.

        Query parameters:
        - limit: Maximum events to return (default: 50, max: 1000)

        Requires: Any authenticated user.
        """
        try:
            data = await control_client.get_events(limit=limit)
            return EventLogResponse(
                events=[EventResponse(**e) for e in data.get("events", [])],
                count=data.get("count", 0),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Control service unavailable: {e}",
            )

    @router.post("/override")
    async def actuator_override(
        actuator_id: str = Query(...),
        state: bool = Query(...),
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        """Override an actuator state.

        Requires: operator or admin role.

        Query parameters:
        - actuator_id: ID of actuator to override
        - state: Desired state (true=on, false=off)
        """
        # Check permission
        if not any(role in current_user.get("roles", []) for role in ["admin", "operator"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only operators and admins can override actuators",
            )

        try:
            return await control_client.override_actuator(actuator_id, state)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Control service unavailable: {e}",
            )

    return router
