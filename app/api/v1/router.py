from fastapi import APIRouter

from app.api.v1.endpoints import (
    base_router,
)

__all__: list[str] = [
    "router",
]

router = APIRouter()

# Include all routers
router.include_router(base_router)
