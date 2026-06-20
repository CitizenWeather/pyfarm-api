"""Response models for pyfarm-api."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SensorReadingResponse(BaseModel):
    """Sensor reading response."""

    sensor_id: str
    metric: str
    value: float
    unit: str
    timestamp: datetime


class ActuatorStateResponse(BaseModel):
    """Actuator state response."""

    name: str
    state: bool
    timestamp: datetime
    last_toggled_at: datetime | None = None


class EventResponse(BaseModel):
    """Control event response."""

    kind: str
    message: str
    timestamp: datetime
    data: dict[str, Any] = Field(default_factory=dict)


class ControlStatusResponse(BaseModel):
    """Current control status."""

    run_id: str
    spec_name: str
    current_stage: str
    elapsed_days: float
    readings: dict[str, Any]
    derived: dict[str, Any]
    actuator_states: dict[str, Any]
    recent_events: list[dict[str, Any]] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    """Historical readings response."""

    readings: list[SensorReadingResponse]
    count: int
    sensor_id: str | None = None
    metric: str | None = None


class EventLogResponse(BaseModel):
    """Event log response."""

    events: list[EventResponse]
    count: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    control_url: str | None = None
    auth_url: str | None = None
    storage_backend: str | None = None


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
