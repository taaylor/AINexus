from datetime import datetime

from pydantic import Field

from auth.src.presentation.api.v1.schemes.base import BaseSchema


class UserRefreshInputSchema(BaseSchema):
    refresh_token: str = Field(min_length=1)


class UserRefreshOutputSchema(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_token_expires_at: datetime
