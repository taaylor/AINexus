from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as PGUUID
from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declarative_mixin,
    declared_attr,
    mapped_column,
)
from uuid_extensions import uuid7

from auth.common.settings import settings
from auth.common.utils import datetime_with_tz


class BaseModel(DeclarativeBase, AsyncAttrs):
    __tablename__: str | None
    __abstract__: bool

    metadata = MetaData(
        schema=settings.postgres.dbschema,
        naming_convention=settings.postgres.idx_naming_convention,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        onupdate=datetime_with_tz,
    )

    repr_cols_num: int = 3
    repr_cols: tuple[str, ...] = ()

    def __repr__(self) -> str:
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


@declarative_mixin
class IdentifiableMixin:
    @declared_attr
    def id(cls) -> Mapped[UUID]:
        return mapped_column(
            PGUUID(as_uuid=True),
            primary_key=True,
            default=uuid7,
        )
