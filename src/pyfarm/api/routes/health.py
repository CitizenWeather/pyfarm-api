"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from pyfarm.config import get_settings

from ..models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        control_url=str(settings.control_url),
        auth_url=str(settings.auth_url),
        storage_backend=settings.storage_backend,
    )
