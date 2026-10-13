from typing import Any

from dishka import Provider, Scope, provide

from auth.common.settings import Settings
from auth.domain.ports import IHasher
from auth.infrastructure.hasher.argon2 import Argon2Hasher


class HasherProvider(Provider):
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
    def hasher(self) -> IHasher:
        return Argon2Hasher(settings=self.settings)
