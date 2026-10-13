from dataclasses import fields, is_dataclass

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    TypeAdapter,
    ValidationError,
)

from auth.common.exceptions.presenter import DTOValidationException


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    def to_dto[TDto](self, dto_type: type[TDto]) -> TDto:
        """Convert schema values into a validated dataclass DTO.

        Only values whose names match ``init=True`` fields in ``dto_type`` are
        passed to the DTO. This allows API-only fields to stay in the schema;
        required DTO fields that have no matching schema value fail validation.

        Args:
            dto_type: The dataclass type to construct from this schema.

        Returns:
            A validated instance of ``dto_type``.

        Raises:
            TypeError: If ``dto_type`` is not a dataclass type.
            DTOValidationException: If the collected values cannot construct a
                valid DTO, for example when a required DTO field is missing.

        Examples:
            >>> from dataclasses import dataclass
            >>> from auth.presentation.api.v1.schemes.base import BaseSchema
            >>> @dataclass
            ... class RegisterInput:
            ...     username: str
            ...     email: str
            >>> class RegisterSchema(BaseSchema):
            ...     username: str
            ...     email: str
            ...     password_repeat: str
            >>> schema = RegisterSchema(
            ...     username="ada", email="ada@example.com", password_repeat="secret"
            ... )
            >>> schema.to_dto(RegisterInput)
            RegisterInput(username='ada', email='ada@example.com')
        """

        if not isinstance(dto_type, type) or not is_dataclass(dto_type):
            raise TypeError("dto_type must be a dataclass type")

        values = self.model_dump(mode="python")

        dto_data = {
            field.name: values[field.name]
            for field in fields(dto_type)
            if field.init and field.name in values
        }

        try:
            return TypeAdapter(dto_type).validate_python(dto_data)
        except ValidationError as exc:
            raise DTOValidationException(
                errors=exc.errors(include_context=False, include_input=False),
            ) from exc


class PaginationSchema(BaseSchema):
    limit: PositiveInt = Field(ge=1, le=100, default=10)
    page: PositiveInt = Field(ge=1, default=1)
