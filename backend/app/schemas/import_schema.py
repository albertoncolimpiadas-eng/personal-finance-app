from decimal import Decimal

from sqlmodel import SQLModel

from app.models.transaction import TransactionType


class TransactionCsvPreviewRow(SQLModel):
    row_number: int
    date: str
    description: str
    amount: str
    account_name: str
    category_name: str | None
    transaction_type: str
    valid: bool
    errors: list[str]


class TransactionCsvPreview(SQLModel):
    rows: list[TransactionCsvPreviewRow]
    valid_count: int
    invalid_count: int


class TransactionCsvImportResult(SQLModel):
    imported_count: int
    skipped_count: int
    rows: list[TransactionCsvPreviewRow]


class ParsedTransactionCsvRow(SQLModel):
    row_number: int
    date: str
    description: str
    amount: Decimal
    account_id: int
    category_id: int | None
    transaction_type: TransactionType
