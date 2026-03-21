import importlib

import pytest
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

import app.main as main_module
from app.core.config import get_settings
from app.enums.error_codes import ErrorCodes


def test_force_https_registers_https_redirect_middleware(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cover `FORCE_HTTPS` branch in `app.main` (HTTPS redirect middleware)."""
    monkeypatch.setenv("FORCE_HTTPS", "true")

    get_settings.cache_clear()
    importlib.reload(main_module)
    try:
        assert any(
            m.cls == HTTPSRedirectMiddleware for m in main_module.app.user_middleware
        )
    finally:
        monkeypatch.delenv("FORCE_HTTPS", raising=False)
        get_settings.cache_clear()
        importlib.reload(main_module)


def test_core_error_handler(client):
    response = client.get("/raise-core-error")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "CoreError"
    assert data["message"] == "fail"
    assert data["code"] == ErrorCodes.CLIENT_INITIALIZATION_ERROR
    assert data["details"] == {"foo": "bar"}
