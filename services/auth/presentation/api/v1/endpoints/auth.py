from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi.routing import APIRouter
from starlette import status

from auth.application.dto.user_register import UserRegisterInput
from auth.application.use_cases.auth.register import UserRegisterUseCase
from auth.presentation.api.v1.schemes.user_register import (
    UserRegisterInputSchema,
    UserRegisterOutputSchema,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    route_class=DishkaRoute,
)


@router.post(
    "/register",
    response_model=UserRegisterOutputSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
async def register_user(
    input_data: UserRegisterInputSchema,
    use_case: FromDishka[UserRegisterUseCase],
) -> UserRegisterOutputSchema:
    output_data = await use_case.execute(
        input_data=input_data.to_dto(UserRegisterInput),
    )
    return UserRegisterOutputSchema.model_validate(output_data)
