from sqlalchemy import Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from auth.infrastructure.database.bsmodel import BaseModel, IdentifiableMixin


class UserModel(BaseModel, IdentifiableMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)

    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    surname: Mapped[str | None] = mapped_column(Text, nullable=True)
    patronymic: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_verified_email: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
