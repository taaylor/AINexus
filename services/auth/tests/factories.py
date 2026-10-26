from datetime import UTC, datetime, timedelta
from typing import Any, override
from uuid import uuid4

from polyfactory import PostGenerated, Use
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from pydantic import BaseModel

from auth.src.infrastructure.database.models import UserModel, UserSessionModel
from auth.src.presentation.api.v1.schemes.user_register import UserRegisterInputSchema
from auth.tests.types import AnyJSON, AnyKwargs


class BaseModelFactory[T: BaseModel](ModelFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def build_json(cls, **kwargs: Any) -> AnyJSON:
        return cls.build(**kwargs).model_dump(mode="json", by_alias=True)

    @classmethod
    def build_python(cls, **kwargs: Any) -> AnyKwargs:
        return cls.build(**kwargs).model_dump()


class BasePatchModelFactory[T: BaseModel](BaseModelFactory[T]):
    __is_base_factory__ = True

    @classmethod
    @override
    def build_json(cls, **kwargs: Any) -> AnyJSON:
        return cls.build(**kwargs).model_dump(
            mode="json", by_alias=True, exclude_defaults=True
        )

    @classmethod
    @override
    def build_python(cls, **kwargs: Any) -> AnyKwargs:
        return cls.build(**kwargs).model_dump(exclude_defaults=True)


class UserModelFactory(SQLAlchemyFactory[UserModel]):
    __model__ = UserModel
    __set_primary_key__ = False
    __set_foreign_keys__ = False
    __set_relationships__ = False

    username = Use(SQLAlchemyFactory.__faker__.unique.user_name)
    name = Use(SQLAlchemyFactory.__faker__.first_name)
    surname = Use(SQLAlchemyFactory.__faker__.last_name)
    patronymic: str | None = None
    is_platform_admin = False
    avatar_key: str | None = None


class UserSessionModelFactory(SQLAlchemyFactory[UserSessionModel]):
    __model__ = UserSessionModel
    __set_primary_key__ = False
    __set_foreign_keys__ = False
    __set_relationships__ = False

    user_id = Use(uuid4)
    refresh_token = Use(SQLAlchemyFactory.__faker__.unique.sha256)
    revoked_at: datetime | None = None
    user_agent = Use(SQLAlchemyFactory.__faker__.user_agent)
    ip_address = Use(SQLAlchemyFactory.__faker__.ipv4)
    expires_at = Use(lambda: datetime.now(UTC) + timedelta(days=30))


def _password_repeat(_name: str, values: dict[str, Any]) -> str:
    return values["password"]


class UserRegisterInputSchemaFactory(BaseModelFactory[UserRegisterInputSchema]):
    __model__ = UserRegisterInputSchema

    username = Use(BaseModelFactory.__faker__.unique.user_name)
    email = Use(BaseModelFactory.__faker__.unique.email)

    password = Use(BaseModelFactory.__faker__.password)
    password_repeat = PostGenerated(_password_repeat)
