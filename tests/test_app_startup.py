from fastapi.testclient import TestClient

from app.enums.error_codes import ErrorCodes
from app.exceptions.core_exception import CoreError
from app.main import app


def test_core_error_handler():
    # Add a temporary route for testing
    @app.get("/raise-core-error")
    async def raise_core_error():
        raise CoreError("fail", ErrorCodes.CLIENT_INITIALIZATION_ERROR, {"foo": "bar"})

    client = TestClient(app)
    response = client.get("/raise-core-error")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "CoreError"
    assert data["message"] == "fail"
    assert data["code"] == ErrorCodes.CLIENT_INITIALIZATION_ERROR
    assert data["details"] == {"foo": "bar"}
