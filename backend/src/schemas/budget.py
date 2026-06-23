from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


CurrencyCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=3,
        to_upper=True,
        pattern=r"^[A-Z]{3}$",
    ),
]


class BudgetBase(BaseModel):
    category_id: int = Field(gt=0)
    amount: Decimal = Field(
        gt=0,
        max_digits=18,
        decimal_places=2,
    )
    currency: CurrencyCode = "dkk"
    period_start: date
    period_end: date

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError(
                "period_end must be on or after period_start"
            )
        return self


class BudgetCreate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
