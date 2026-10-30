from typing import Final, Self

from faker import Faker


class FakerExt:
    _instance: Self | None = None

    def __new__(cls) -> Self:

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.faker = Faker()
            self._initialized = True


fake: Final[FakerExt] = FakerExt()
