from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator


CategoryName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=55),
]


class CategoryCreate(BaseModel):
    name: CategoryName
    category_type: Literal["expense", "income"] = "expense"


class CategoryRead(BaseModel):
    id: int
    name: str
    category_type: Literal["expense", "income"]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    name: CategoryName | None = None
    category_type: Literal["expense", "income"] | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def require_non_null_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Updated fields cannot be null")
        return self
