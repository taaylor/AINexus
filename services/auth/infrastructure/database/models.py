from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from auth.infrastructure.database.bsmodel import BaseModel, IdentifiableMixin


class UserModel(BaseModel, IdentifiableMixin):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("id", "organization_id"),)

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    surname: Mapped[str | None] = mapped_column(String, nullable=True)
    patronymic: Mapped[str | None] = mapped_column(String, nullable=True)

    is_platform_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
    avatar_key: Mapped[str | None] = mapped_column(String, nullable=True)

    organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )


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


class RoleModel(BaseModel, IdentifiableMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class OrganizationModel(BaseModel, IdentifiableMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class PermissionModel(BaseModel, IdentifiableMixin):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


class RolePermissionModel(BaseModel, IdentifiableMixin):
    __tablename__ = "roles_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "permissions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


class UserRoleAssignmentModel(BaseModel, IdentifiableMixin):
    __tablename__ = "user_role_assignments"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


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
