from pydantic import BaseModel, PositiveInt

from auth.src.presentation.api.v1.schemes.user_register import (
    UserRegisterInputSchema,
    UserRegisterOutputSchema,
)


class SeedsPlan(BaseModel):
    users_count: PositiveInt = 10


class SeededUser(BaseModel):
    registration_input: UserRegisterInputSchema
    registration_output: UserRegisterOutputSchema


class SeedsResult(BaseModel):
    users: list[SeededUser]
