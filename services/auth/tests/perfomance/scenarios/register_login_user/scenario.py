from uuid import uuid4

from locust import task

from auth.src.presentation.api.v1.schemes.user_login import (
    UserLoginInputSchema,
    UserLoginOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_profile import (
    UserProfileOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_refresh import (
    UserRefreshInputSchema,
    UserRefreshOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_register import (
    UserRegisterInputSchema,
    UserRegisterOutputSchema,
)
from auth.src.presentation.api.v1.schemes.user_sessions import (
    UserListSessionsOutputSchema,
)
from auth.tests.perfomance.tools.locust.tasks import BaseLocustSequentialTaskSet
from auth.tests.perfomance.tools.locust.user import BaseLocustUser


class UserFlowSequentialTaskSet(BaseLocustSequentialTaskSet):
    register_input: UserRegisterInputSchema | None = None
    register_output: UserRegisterOutputSchema | None = None
    login_output: UserLoginOutputSchema | None = None
    refresh_output: UserRefreshOutputSchema | None = None
    profile_output: UserProfileOutputSchema | None = None
    sessions_output: UserListSessionsOutputSchema | None = None

    @task
    def register_user(self) -> None:
        password = self.fake.password(length=12)
        user_id = uuid4().hex

        self.register_input = UserRegisterInputSchema(
            username=f"locust_{user_id[:23]}",
            email=f"locust-{user_id}@load.test",
            password=password,
            password_repeat=password,
            surname=self.fake.name(),
            name=self.fake.name(),
            patronymic=self.fake.name(),
            telegram=self.fake.user_name(),
        )

        self.register_output = self.auth_client.register_user(self.register_input)

    @task
    def login_user(self) -> None:
        if self.register_output is None or self.register_input is None:
            return
        self.login_output = self.auth_client.login_user(
            UserLoginInputSchema(
                login=self.register_output.username,
                password=self.register_input.password,
            )
        )

    @task
    def refresh_user(self) -> None:
        if self.login_output is None:
            return
        self.refresh_output = self.auth_client.refresh_user(
            UserRefreshInputSchema(refresh_token=self.login_output.refresh_token)
        )

    @task
    def fetch_user_profile(self) -> None:
        if self.refresh_output is None:
            return
        self.profile_output = self.auth_client.fetch_user_profile(
            headers={"Authorization": f"Bearer {self.refresh_output.access_token}"},
        )

    @task
    def list_user_sessions(self) -> None:
        if self.refresh_output is None:
            return
        self.sessions_output = self.auth_client.list_user_sessions(
            headers={"Authorization": f"Bearer {self.refresh_output.access_token}"},
        )

    @task
    def logout_user(self) -> None:
        if self.refresh_output is None:
            return
        self.auth_client.logout_user(
            headers={"Authorization": f"Bearer {self.refresh_output.access_token}"},
        )


class RegisterLoginUser(BaseLocustUser):
    tasks = [UserFlowSequentialTaskSet]
