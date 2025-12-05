import enum

__all__: list[str] = [
    "ErrorCodes",
]


class ErrorCodes(enum.StrEnum):
    CLIENT_INITIALIZATION_ERROR = "CLIENT_INITIALIZATION_ERROR"
