from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserRefreshInput:
    refresh_token: str
