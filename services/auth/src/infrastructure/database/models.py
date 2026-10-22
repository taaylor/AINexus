from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from auth.src.infrastructure.database.bsmodel import BaseModel, IdentifiableMixin


class UserModel(BaseModel, IdentifiableMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    surname: Mapped[str | None] = mapped_column(String, nullable=True)
    patronymic: Mapped[str | None] = mapped_column(String, nullable=True)

    is_platform_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
    avatar_key: Mapped[str | None] = mapped_column(String, nullable=True)


class UserCredentialModel(BaseModel):
    __tablename__ = "users_cred"

    id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    telegram: Mapped[str | None] = mapped_column(String, nullable=True)

    is_verified_email: Mapped[bool] = mapped_column(Boolean, nullable=False)


class UserSessionModel(BaseModel, IdentifiableMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[UUID] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)

    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
