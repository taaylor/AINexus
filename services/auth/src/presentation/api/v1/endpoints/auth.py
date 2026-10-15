from dataclasses import replace
from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import DishkaRoute
from fastapi import Depends
from fastapi.routing import APIRouter
from starlette import status
from starlette.requests import Request

from auth.src.application.dto.user import (
    UserProfileInput,
    UserProfileOutput,
)
from auth.src.application.dto.user_login import UserLoginInput
from auth.src.application.dto.user_register import (
    UserRegisterInput,
    UserRegisterOutput,
)
from auth.src.domain.entities.tokens import TokenPair, TokenPayload
from auth.src.domain.ports import IUseCase
from auth.src.presentation.api.dependencies import auth_user
from auth.src.presentation.api.v1.schemes.user_login import (
    UserLoginInputSchema,
    UserLoginOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_profile import (
    UserProfileOutputSchema,
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
    ip_address = request.client.host if request.client is not None else None

    output_data = await use_case.execute(
        input_data=replace(
            input_data.to_dto(UserLoginInput),
            user_agent=request.headers.get("user-agent"),
            ip_address=ip_address,
        ),
    )

    return UserLoginOutputSchema.model_validate(output_data)


@router.get(
    "/profile",
    response_model=UserProfileOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="Get a user profile",
)
async def fetch_user_profile(
    current_user: Annotated[TokenPayload, Depends(auth_user)],
    use_case: Annotated[
        IUseCase[UserProfileInput, UserProfileOutput],
        FromComponent("user_profile"),
    ],
) -> UserProfileOutputSchema:
    output_data = await use_case.execute(
        input_data=UserProfileInput(user_id=current_user.id),
    )
    return UserProfileOutputSchema.model_validate(output_data)
