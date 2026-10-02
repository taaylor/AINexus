from typing import Literal

from auth.presentation.api.v1.schemes.base import BaseSchema


class HealthResponse(BaseSchema):
    status: Literal["ok", "error"]
    ip_address: str | None
    port: int | None
    user_agent: str | None
