"""Health check endpoints."""

from __future__ import annotations

import os

from fastapi import APIRouter

from ..models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        control_url=os.getenv("CONTROL_URL", "http://localhost:8000"),
        auth_url=os.getenv("AUTH_URL", "http://localhost:8001"),
        storage_backend=os.getenv("PYFARM_STORAGE_BACKEND", "sqlite"),
    )
