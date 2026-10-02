from typing import Any

from dishka import Provider

from auth.common.settings import Settings


class ApplicationProvider(Provider):
    def __init__(
        self,
        settings: Settings,
        *,
        scope: Any | None = None,
        component: Any | None = None,
        when: Any | None = None,
    ):
        super().__init__(scope, component, when)
        self.settings = settings
