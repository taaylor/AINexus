from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class PaginationSchema(BaseSchema):
    limit: PositiveInt = Field(ge=1, le=100, default=10)
    page: PositiveInt = Field(ge=1, default=1)
