from typing import Any

from dishka import Provider, Scope, provide

from auth.src.common.settings import Settings
from auth.src.domain.ports import ITokenProvider
from auth.src.infrastructure.jwt.jwt_coder import JWTCoder


class JwtProvider(Provider):
    def __init__(
        self,
        settings: Settings,
        *,
        scope: Any | None = None,
        component: Any | None = None,
        when: Any | None = None,
    ) -> None:
        super().__init__(scope, component, when)
        self.settings = settings

    @provide(scope=Scope.APP)
    def jwt_coder(self) -> ITokenProvider:
        return JWTCoder(settings=self.settings)
