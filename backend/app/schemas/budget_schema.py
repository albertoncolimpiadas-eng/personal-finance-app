from datetime import datetime
from decimal import Decimal

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models.category import CategoryType


class BudgetBase(SQLModel):
    category_id: int
    year: int
    month: int
    limit_amount: Decimal

    @field_validator("year")
    @classmethod
    def year_must_be_reasonable(cls, value: int) -> int:
        if value < 1900 or value > 2200:
            raise ValueError("year must be between 1900 and 2200")
        return value

    @field_validator("month")
    @classmethod
    def month_must_be_valid(cls, value: int) -> int:
        if value < 1 or value > 12:
            raise ValueError("month must be between 1 and 12")
        return value

    @field_validator("limit_amount")
    @classmethod
    def limit_amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("limit_amount must be greater than 0")
        return value


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    id: int
    created_at: datetime


class BudgetCategoryRead(SQLModel):
    id: int
    name: str
    type: CategoryType
    color: str


class BudgetMonthlySummary(SQLModel):
    category: BudgetCategoryRead
    limit_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal
