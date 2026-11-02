from faker import Faker

from auth.src.presentation.api.v1.schemes.user_register import UserRegisterInputSchema
from auth.tests.perfomance.api.auth_client import AuthApiClient
from auth.tests.perfomance.seeds.models import SeededUser, SeedsPlan, SeedsResult


class SeedsBuilder:
    def __init__(
        self,
        auth_api_client: AuthApiClient,
        faker: Faker | None = None,
    ) -> None:
        self._auth_api_client = auth_api_client
        self._faker = faker or Faker()

    async def build(self, *, plan: SeedsPlan) -> SeedsResult:
        users: list[SeededUser] = []

        for _ in range(plan.users_count):
            registration_input = self._build_registration_input()
            registration_output = await self._auth_api_client.register_user(
                input_data=registration_input,
            )
            users.append(
                SeededUser(
                    registration_input=registration_input,
                    registration_output=registration_output,
                ),
            )

        return SeedsResult(users=users)

    def _build_registration_input(self) -> UserRegisterInputSchema:
        password = self._faker.password(length=32)

        return UserRegisterInputSchema(
            username=self._faker.company_email()[:29],
            email=self._faker.company_email(),
            password=password,
            password_repeat=password,
            name=self._faker.first_name(),
            surname=self._faker.last_name(),
        )
