from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import DishkaRoute
from fastapi.routing import APIRouter
from starlette import status

from auth.src.application.dto.user_sessions import (
    UserListSessionsInput,
    UserListSessionsOutput,
)
from auth.src.domain.ports import IUseCase
from auth.src.presentation.api.v1.dependencies import AuthUserProxy
from auth.src.presentation.api.v1.schemes.user_sessions import (
    UserListSessionsOutputSchema,
)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
    route_class=DishkaRoute,
)


@router.get(
    "",
    response_model=UserListSessionsOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="List the current user's sessions",
)
async def list(
    current_user: AuthUserProxy,
    use_case: Annotated[
        IUseCase[UserListSessionsInput, UserListSessionsOutput],
        FromComponent("user_list_sessions"),
    ],
) -> UserListSessionsOutputSchema:
    output_data = await use_case.execute(
        input_data=UserListSessionsInput(user_id=current_user.user_id),
    )
    return UserListSessionsOutputSchema.model_validate(output_data)
