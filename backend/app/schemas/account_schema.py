from datetime import datetime
from decimal import Decimal

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models.account import AccountType


class AccountBase(SQLModel):
    name: str
    type: AccountType
    currency: str = "EUR"
    initial_balance: Decimal = Decimal("0")

    @field_validator("name")
    @classmethod
    def name_cannot_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value

    @field_validator("currency")
    @classmethod
    def currency_cannot_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("currency cannot be empty")
        return value.upper()


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int
    created_at: datetime
