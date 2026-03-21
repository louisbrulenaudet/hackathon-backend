from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "PingResponse",
    "HealthResponse",
]


class PingResponse(BaseModel):
    model_config = ConfigDict(frozen=True, title="PingResponse")
    status: Literal["ok"] = Field(
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


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, title="HealthResponse")
    status: Literal["ok"] = Field(
        default="ok",
        description="The health status of the service.",
    )
