from typing import Literal

from auth.presentation.api.v1.schemes.base import BaseSchema


class HealthResponse(BaseSchema):
    status: Literal["ok", "error"]
