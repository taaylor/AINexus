from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserLoginInput:
    login: str
    password: str
    user_agent: str | None = None
    ip_address: str | None = None
