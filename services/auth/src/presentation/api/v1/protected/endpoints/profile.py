from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import DishkaRoute
from fastapi.routing import APIRouter
from starlette import status

from auth.src.application.dto.user import UserProfileInput, UserProfileOutput
from auth.src.domain.ports import IUseCase
from auth.src.presentation.api.v1.dependencies import AuthUserProxy
from auth.src.presentation.api.v1.schemes.user_profile import (
    UserProfileOutputSchema,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    route_class=DishkaRoute,
)


@router.get(
    "/profile",
    response_model=UserProfileOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="Get a user profile",
)
async def fetch_user_profile(
    user_proxy: AuthUserProxy,
    use_case: Annotated[
        IUseCase[UserProfileInput, UserProfileOutput],
        FromComponent("user_profile"),
    ],
) -> UserProfileOutputSchema:
    output_data = await use_case.execute(
        input_data=UserProfileInput(user_id=user_proxy.user_id),
    )
    return UserProfileOutputSchema.model_validate(output_data)
