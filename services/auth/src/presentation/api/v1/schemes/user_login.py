from datetime import datetime

from auth.src.presentation.api.v1.schemes.base import BaseSchema


class UserLoginInputSchema(BaseSchema):
    login: str
    password: str


class UserLoginOutputSchema(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_token_expires_at: datetime
