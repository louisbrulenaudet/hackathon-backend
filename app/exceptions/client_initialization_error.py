from app.enums.error_codes import ErrorCodes
from app.exceptions.core_exception import CoreError

__all__ = [
    "ClientInitializationError",
]


class ClientInitializationError(CoreError):
    http_status_code: int = 500

    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The client initialization failed.",
            ErrorCodes.CLIENT_INITIALIZATION_ERROR,
            details=str(details),
        )
