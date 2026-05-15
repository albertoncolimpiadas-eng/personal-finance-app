import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import StringIO

from sqlmodel import Session

from app.models.category import CategoryType
from app.models.transaction import TransactionType
from app.repositories import account_repository, category_repository
from app.schemas.import_schema import (
    ParsedTransactionCsvRow,
    TransactionCsvImportResult,
    TransactionCsvPreview,
    TransactionCsvPreviewRow,
)
from app.schemas.transaction_schema import TransactionCreate
from app.services import transaction_service

EXPECTED_COLUMNS = {
    "date",
    "description",
    "amount",
    "account_name",
    "category_name",
    "transaction_type",
}
TRADE_REPUBLIC_COLUMNS = {"date", "account_type", "category", "type", "amount", "description"}
INCOME_TYPES = {"BENEFITS_SAVEBACK", "CUSTOMER_INBOUND", "INTEREST_PAYMENT"}


def preview_transactions_csv(session: Session, content: bytes) -> TransactionCsvPreview:
    rows = parse_preview_rows(session, content)
    return TransactionCsvPreview(
        rows=rows,
        valid_count=sum(1 for row in rows if row.valid),
        invalid_count=sum(1 for row in rows if not row.valid),
    )


def confirm_transactions_csv(session: Session, content: bytes) -> TransactionCsvImportResult:
    preview_rows = parse_preview_rows(session, content)
    imported_count = 0

    for row in preview_rows:
        if not row.valid:
            continue
        parsed = parse_valid_row(session, row)
        transaction_service.create_transaction(
            session,
            TransactionCreate(
                transaction_type=parsed.transaction_type,
                amount=parsed.amount,
                date=date.fromisoformat(parsed.date),
                description=parsed.description,
                account_id=parsed.account_id,
                category_id=parsed.category_id,
            ),
        )
        imported_count += 1

    return TransactionCsvImportResult(
        imported_count=imported_count,
        skipped_count=len(preview_rows) - imported_count,
        rows=preview_rows,
    )


def parse_preview_rows(session: Session, content: bytes) -> list[TransactionCsvPreviewRow]:
    text = content.decode("utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(StringIO(text), dialect=dialect)
    if reader.fieldnames is None:
        return []

    fieldnames = set(reader.fieldnames)
    is_trade_republic = TRADE_REPUBLIC_COLUMNS.issubset(fieldnames)
    missing_columns = set() if is_trade_republic else EXPECTED_COLUMNS - fieldnames
    rows: list[TransactionCsvPreviewRow] = []
    for row_number, raw_row in enumerate(reader, start=2):
        row = normalize_trade_republic_row(raw_row) if is_trade_republic else normalize_row(raw_row)
        errors = validate_row(session, row)
        if missing_columns:
            errors = [f"missing columns: {', '.join(sorted(missing_columns))}", *errors]
        rows.append(
            TransactionCsvPreviewRow(
                row_number=row_number,
                date=row["date"],
                description=row["description"],
                amount=row["amount"],
                account_name=row["account_name"],
                category_name=row["category_name"] or None,
                transaction_type=row["transaction_type"],
                valid=len(errors) == 0,
                errors=errors,
            )
        )
    return rows


def normalize_row(raw_row: dict[str, str | None]) -> dict[str, str]:
    return {column: (raw_row.get(column) or "").strip() for column in EXPECTED_COLUMNS}


def normalize_trade_republic_row(raw_row: dict[str, str | None]) -> dict[str, str]:
    amount = parse_trade_republic_amount((raw_row.get("amount") or "").strip())
    return {
        "date": normalize_trade_republic_date((raw_row.get("date") or "").strip()),
        "description": (raw_row.get("description") or "").strip(),
        "amount": str(abs(amount)) if amount is not None else (raw_row.get("amount") or "").strip(),
        "account_name": (raw_row.get("account_type") or "").strip(),
        "category_name": (raw_row.get("category") or "").strip(),
        "transaction_type": infer_trade_republic_transaction_type(
            (raw_row.get("type") or "").strip(),
            amount,
        ),
    }


def normalize_trade_republic_date(value: str) -> str:
    try:
        day, month, year = value.split("/")
        return date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return value


def parse_trade_republic_amount(value: str) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        compact = value.replace(".", "")
        try:
            amount = Decimal(compact)
        except InvalidOperation:
            return None
        if abs(amount) >= Decimal("1000000"):
            return amount / Decimal("1000000")
        return amount


def infer_trade_republic_transaction_type(value: str, amount: Decimal | None) -> str:
    if value in INCOME_TYPES:
        return TransactionType.INCOME.value
    if amount is not None and amount < 0:
        return TransactionType.EXPENSE.value
    if amount is not None and amount > 0:
        return TransactionType.INCOME.value
    return value


def validate_row(session: Session, row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    try:
        date.fromisoformat(row["date"])
    except ValueError:
        errors.append("date must be a valid ISO date")

    try:
        amount = Decimal(row["amount"])
        if amount <= 0:
            errors.append("amount must be greater than 0")
    except InvalidOperation:
        errors.append("amount must be a valid decimal")

    if not row["description"]:
        errors.append("description is required")

    account = account_repository.get_account_by_name(session, row["account_name"])
    if account is None:
        errors.append("account must exist")

    try:
        transaction_type = TransactionType(row["transaction_type"])
    except ValueError:
        errors.append("transaction_type must be income, expense, or transfer")
        return errors

    if transaction_type == TransactionType.TRANSFER:
        errors.append("transfer import requires target account support")
        return errors

    category = category_repository.get_category_by_name(session, row["category_name"])
    if category is None:
        errors.append("category must exist")
    elif transaction_type == TransactionType.INCOME and category.type != CategoryType.INCOME:
        errors.append("income transaction must use income category")
    elif transaction_type == TransactionType.EXPENSE and category.type != CategoryType.EXPENSE:
        errors.append("expense transaction must use expense category")

    return errors


def parse_valid_row(session: Session, row: TransactionCsvPreviewRow) -> ParsedTransactionCsvRow:
    account = account_repository.get_account_by_name(session, row.account_name)
    category = category_repository.get_category_by_name(session, row.category_name or "")
    if account is None:
        raise ValueError("account must exist")
    if category is None:
        raise ValueError("category must exist")

    return ParsedTransactionCsvRow(
        row_number=row.row_number,
        date=row.date,
        description=row.description,
        amount=Decimal(row.amount),
        account_id=account.id,
        category_id=category.id,
        transaction_type=TransactionType(row.transaction_type),
    )
