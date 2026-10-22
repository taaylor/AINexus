from typing import Final

from auth.src.application.dto.user import UserProfileInput, UserProfileOutput
from auth.src.common.exceptions import NotFoundException
from auth.src.domain.ports import IUseCase
from auth.src.domain.ports.repository.users_repo import IUsersRepository


class UserProfileUseCase(IUseCase[UserProfileInput, UserProfileOutput]):
    __slots__: Final[tuple[str, ...]] = ("_users_repository",)

    def __init__(self, *, users_repository: IUsersRepository) -> None:
        self._users_repository = users_repository

    async def execute(
        self,
        *,
        input_data: UserProfileInput,
    ) -> UserProfileOutput:
        profile = await self._users_repository.fetch_by_id_profile(
            user_id=input_data.user_id,
        )

        if profile is None:
            raise NotFoundException("User profile not found")

        return UserProfileOutput(
            id=profile.id,
            username=profile.username,
            name=profile.name,
            surname=profile.surname,
            patronymic=profile.patronymic,
            avatar_key=profile.avatar_key,
            email=profile.email,
            telegram=profile.telegram,
            is_verified_email=profile.is_verified_email,
        )
