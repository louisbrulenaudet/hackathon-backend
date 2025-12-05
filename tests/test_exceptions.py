from app.enums.error_codes import ErrorCodes
from app.exceptions.client_initialization_error import ClientInitializationError
from app.exceptions.core_exception import CoreError


def test_core_error_str_and_dict():
    err = CoreError("msg", ErrorCodes.CLIENT_INITIALIZATION_ERROR, {"foo": "bar"})
    s = str(err)
    d = err.to_dict()
    assert "CoreError" in s
    assert d["error"] == "CoreError"
    assert d["message"] == "msg"
    assert d["code"] == ErrorCodes.CLIENT_INITIALIZATION_ERROR
    assert d["details"] == {"foo": "bar"}


def test_core_error_no_details():
    err = CoreError("msg", ErrorCodes.CLIENT_INITIALIZATION_ERROR)
    d = err.to_dict()
    assert d["details"] == {}


def test_client_initialization_error():
    err = ClientInitializationError("fail")
    assert isinstance(err, CoreError)
    assert err.message == "The client initialization failed."
    assert err.code == ErrorCodes.CLIENT_INITIALIZATION_ERROR
    assert isinstance(err.details, str) and "fail" in err.details
