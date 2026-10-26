from uuid import UUID

from auth.src.presentation.api.v1.schemes.base import BaseSchema


class UserSessionOutputSchema(BaseSchema):
    id: UUID
    user_agent: str | None
    ip_address: str | None


class UserListSessionsOutputSchema(BaseSchema):
    active: list[UserSessionOutputSchema]
    inactive: list[UserSessionOutputSchema]
