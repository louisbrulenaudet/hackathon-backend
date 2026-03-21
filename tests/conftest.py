from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.enums.error_codes import ErrorCodes
from app.exceptions.core_exception import CoreError
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _register_core_error_test_route() -> None:
    """Register a stable test route once to avoid mutating `app` per test."""
    if any(getattr(route, "path", None) == "/raise-core-error" for route in app.routes):
        return

    @app.get("/raise-core-error")
    async def raise_core_error() -> None:
        raise CoreError(
            "fail",
            ErrorCodes.CLIENT_INITIALIZATION_ERROR,
            {"foo": "bar"},
        )


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    """Reusable TestClient that triggers the app lifespan (startup/shutdown)."""

    with TestClient(app) as client:
        yield client
