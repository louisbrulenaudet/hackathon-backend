from pydantic import BaseModel, Field

__all__: list[str] = [
    "PingResponse",
]


class PingResponse(BaseModel):
    status: str = Field(
        default="ok",
        description="The status of the health check.",
    )
    uptime: int = Field(
        default=0,
        description="The uptime of the service in seconds.",
    )
    timestamp: int = Field(
        default=0,
        description="The current timestamp when the health check was performed.",
    )
