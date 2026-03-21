import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from aiocache import caches
from aiocache.backends.memory import SimpleMemoryCache
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_router
from app.core.config import get_settings
from app.exceptions.core_exception import CoreError

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """
    Lifespan configuration for the FastAPI application, setting up the cache configuration.
    """
    caches.set_config(
        {"default": {"cache": SimpleMemoryCache, "ttl": 60, "maxsize": 1000}}
    )
    yield


app = FastAPI(
    title=settings.name,
    description="Hackathon backend based on FastAPI and Pydantic validation designed to ship fast, fast, fast 🏎️",
    version=settings.version,
    lifespan=lifespan,
)

# Add CORS middleware to allow all origins and methods for local network access. Do not use outside hackathon projects or for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
    expose_headers=["X-Request-ID"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1500,
    compresslevel=5,
)
app.include_router(api_router, prefix="/api/v1")

if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)


@app.exception_handler(CoreError)
async def error_handler(_: Request, exc: CoreError) -> JSONResponse:
    """
    Custom exception handler for `CoreError`.
    Converts the error into a structured JSON response.
    """
    # Default to 400 if not specified on the exception class.
    status_code: int = getattr(exc.__class__, "http_status_code", 400)

    logger.error(
        "CoreError: %s [Code: %s] Details: %s",
        exc.message,
        exc.code,
        exc.details,
    )

    payload: dict[str, Any] = {
        "error": exc.__class__.__name__,
        "message": exc.message,
        "code": exc.code,
        "details": exc.details or {},
    }

    return JSONResponse(
        status_code=status_code,
        content=payload,
    )
