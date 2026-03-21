from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI

__all__ = [
    "get_app",
]


def get_app() -> FastAPI:
    """Return the FastAPI application lazily."""
    from app.main import app

    return app
