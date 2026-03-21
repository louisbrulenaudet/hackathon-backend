from app.enums.error_codes import ErrorCodes


def test_core_error_handler(client):
    response = client.get("/raise-core-error")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "CoreError"
    assert data["message"] == "fail"
    assert data["code"] == ErrorCodes.CLIENT_INITIALIZATION_ERROR
    assert data["details"] == {"foo": "bar"}
