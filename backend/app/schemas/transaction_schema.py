from datetime import date, datetime
from decimal import Decimal

from pydantic import field_validator, model_validator
from sqlmodel import SQLModel

from app.models.transaction import TransactionType


class TransactionBase(SQLModel):
    transaction_type: TransactionType
    amount: Decimal
    date: date
    description: str
    account_id: int
    category_id: int | None = None
    target_account_id: int | None = None
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("amount must be greater than 0")
        return value

    @field_validator("description")
    @classmethod
    def description_cannot_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be empty")
        return value

    @field_validator("notes")
    @classmethod
    def blank_notes_becomes_none(cls, value: str | None) -> str | None:
        if value is None:
            return None

        notes = value.strip()
        return notes or None

    @model_validator(mode="after")
    def validate_required_relationships(self) -> "TransactionBase":
        if self.transaction_type in {TransactionType.INCOME, TransactionType.EXPENSE}:
            if self.category_id is None:
                raise ValueError("category_id is required for income and expense transactions")
            if self.target_account_id is not None:
                raise ValueError("target_account_id must be empty for income and expense transactions")

        if self.transaction_type == TransactionType.TRANSFER:
            if self.target_account_id is None:
                raise ValueError("target_account_id is required for transfer transactions")

        return self


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
