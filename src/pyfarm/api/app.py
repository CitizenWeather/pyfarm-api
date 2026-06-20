"""FastAPI application for pyfarm API gateway."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from pyfarm.auth.security import decode_access_token

from .client import ControlClient, get_control_client
from .models import HealthResponse
from .routes import control, health

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Get authenticated user from JWT token.

    Returns user info dict with keys: user_id, username, roles.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return {
        "user_id": payload.user_id,
        "username": payload.sub,
        "roles": payload.roles,
    }


def create_app(control_client: ControlClient | None = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        control_client: Optional pre-configured control client.
    """
    app = FastAPI(
        title="pyfarm-api",
        description="API gateway for pyfarm ecosystem",
        version="0.1.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize control client dependency
    if control_client is None:
        control_client_dep = get_control_client()
    else:
        control_client_dep = control_client

    # Health endpoint (no auth required)
    app.include_router(
        health.router,
        prefix="",
        tags=["health"],
    )

    # Control endpoints (auth required)
    app.include_router(
        control.create_router(control_client_dep, get_current_user),
        prefix="/api/v1",
        tags=["control"],
    )

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8002)
