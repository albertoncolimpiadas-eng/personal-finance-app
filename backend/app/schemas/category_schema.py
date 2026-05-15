from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models.category import CategoryType


class CategoryBase(SQLModel):
    name: str
    type: CategoryType
    color: str | None = "#0f766e"

    @field_validator("name")
    @classmethod
    def name_cannot_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value

    @field_validator("color")
    @classmethod
    def blank_color_becomes_none(cls, value: str | None) -> str | None:
        if value is None:
            return "#0f766e"

        color = value.strip()
        return color or "#0f766e"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
