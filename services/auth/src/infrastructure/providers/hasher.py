from typing import Annotated, Any

from dishka import FromComponent, Provider, Scope, provide

from auth.src.common.settings import Settings
from auth.src.domain.ports import IHasher
from auth.src.infrastructure.hasher.argon2 import Argon2Hasher
from auth.src.infrastructure.hasher.sha256 import SHA256Hasher


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

    @provide(
        scope=Scope.APP,
        provides=Annotated[IHasher, FromComponent("argon2")],
    )
    def argon2_hasher(self) -> IHasher:
        return Argon2Hasher(settings=self.settings)

    @provide(
        scope=Scope.APP,
        provides=Annotated[IHasher, FromComponent("sha256")],
    )
    def sha256_hasher(self) -> IHasher:
        return SHA256Hasher()
