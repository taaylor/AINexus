from uuid import UUID

from auth.src.presentation.api.v1.schemes.base import BaseSchema


class UserProfileOutputSchema(BaseSchema):
    id: UUID
    username: str
    name: str | None
    surname: str | None
    patronymic: str | None
    avatar_key: str | None
    organization_id: UUID | None
    email: str
    telegram: str | None
    is_verified_email: bool
