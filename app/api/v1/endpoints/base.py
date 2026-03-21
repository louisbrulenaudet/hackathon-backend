import time

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.dtos.models import HealthResponse, PingResponse

router = APIRouter(tags=["health"])


@router.get(
    "/ping",
    response_model=PingResponse,
    tags=["Health"],
    summary="Ping endpoint",
    description="Health check endpoint for readiness/liveness probes.",
)
async def ping(settings: Settings = Depends(get_settings)) -> PingResponse:
    """
    Health check endpoint for readiness/liveness probes.
    """
    now: int = int(time.time())
    uptime: int = now - int(settings.service_start_time)

    return PingResponse(
        status="ok",
        uptime=uptime,
        timestamp=now,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Lightweight healthcheck endpoint for Docker/K8s.",
)
async def health() -> HealthResponse:
    """
    Lightweight healthcheck endpoint for Docker/K8s.

    Returns:
        HealthResponse: A structured health status payload.

    Example:
        >>> await health()
        {'status': 'ok'}
    """
    return HealthResponse(status="ok")
