from dataclasses import replace
from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import DishkaRoute
from fastapi.routing import APIRouter
from starlette import status
from starlette.requests import Request

from auth.src.application.dto.user_login import UserLoginInput
from auth.src.application.dto.user_refresh import UserRefreshInput
from auth.src.application.dto.user_register import (
    UserRegisterInput,
    UserRegisterOutput,
)
from auth.src.domain.entities.tokens import TokenPair
from auth.src.domain.ports import IUseCase
from auth.src.presentation.api.v1.schemes.user_login import (
    UserLoginInputSchema,
    UserLoginOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_refresh import (
    UserRefreshInputSchema,
    UserRefreshOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_register import (
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
    use_case: Annotated[
        IUseCase[UserRegisterInput, UserRegisterOutput],
        FromComponent("user_register"),
    ],
) -> UserRegisterOutputSchema:
    output_data = await use_case.execute(
        input_data=input_data.to_dto(UserRegisterInput),
    )
    return UserRegisterOutputSchema.model_validate(output_data)


@router.post(
    "/login",
    response_model=UserLoginOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="Log in a user",
)
async def login_user(
    input_data: UserLoginInputSchema,
    use_case: Annotated[
        IUseCase[UserLoginInput, TokenPair],
        FromComponent("user_login"),
    ],
    request: Request,
) -> UserLoginOutputSchema:
    output_data = await use_case.execute(
        input_data=replace(
            input_data.to_dto(UserLoginInput),
            user_agent=request.headers.get("user-agent"),
            ip_address=(request.client.host if request.client is not None else None),
        ),
    )

    return UserLoginOutputSchema.model_validate(output_data)


@router.post(
    "/refresh",
    response_model=UserRefreshOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="Refresh an access token",
)
async def refresh_user_tokens(
    input_data: UserRefreshInputSchema,
    use_case: Annotated[
        IUseCase[UserRefreshInput, TokenPair],
        FromComponent("user_refresh"),
    ],
) -> UserRefreshOutputSchema:
    output_data = await use_case.execute(
        input_data=input_data.to_dto(UserRefreshInput),
    )
    return UserRefreshOutputSchema.model_validate(output_data)
