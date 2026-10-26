from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import DishkaRoute
from fastapi.routing import APIRouter
from starlette import status

from auth.src.application.dto.user_logout import UserLogoutInput
from auth.src.domain.ports import IUseCase
from auth.src.presentation.api.v1.dependencies import AuthUserProxy

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    route_class=DishkaRoute,
)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out the current session",
)
async def logout_user(
    current_user: AuthUserProxy,
    use_case: Annotated[
        IUseCase[UserLogoutInput, None],
        FromComponent("user_logout"),
    ],
) -> None:
    await use_case.execute(
        input_data=UserLogoutInput(
            session_id=current_user.session_id,
            user_id=current_user.user_id,
        ),
    )
