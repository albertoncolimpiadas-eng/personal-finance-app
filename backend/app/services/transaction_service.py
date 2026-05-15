from datetime import date

from sqlmodel import Session

from app.models.category import CategoryType
from app.models.transaction import Transaction, TransactionType
from app.repositories import account_repository, category_repository, transaction_repository
from app.schemas.transaction_schema import TransactionCreate, TransactionUpdate


class TransactionValidationError(ValueError):
    pass


def list_transactions(
    session: Session,
    account_id: int | None = None,
    category_id: int | None = None,
    transaction_type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    text: str | None = None,
) -> list[Transaction]:
    return transaction_repository.list_transactions(
        session=session,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        date_from=date_from,
        date_to=date_to,
        text=text,
    )


def get_transaction(session: Session, transaction_id: int) -> Transaction | None:
    return transaction_repository.get_transaction(session, transaction_id)


def create_transaction(
    session: Session,
    transaction_create: TransactionCreate,
) -> Transaction:
    validate_transaction(session, transaction_create)
    return transaction_repository.create_transaction(session, transaction_create)


def update_transaction(
    session: Session,
    transaction_id: int,
    transaction_update: TransactionUpdate,
) -> Transaction | None:
    transaction = transaction_repository.get_transaction(session, transaction_id)
    if transaction is None:
        return None

    validate_transaction(session, transaction_update)
    return transaction_repository.update_transaction(session, transaction, transaction_update)


def delete_transaction(session: Session, transaction_id: int) -> bool:
    transaction = transaction_repository.get_transaction(session, transaction_id)
    if transaction is None:
        return False

    transaction_repository.delete_transaction(session, transaction)
    return True


def validate_transaction(
    session: Session,
    transaction_data: TransactionCreate | TransactionUpdate,
) -> None:
    source_account = account_repository.get_account(session, transaction_data.account_id)
    if source_account is None:
        raise TransactionValidationError("account_id does not reference an existing account")

    if transaction_data.transaction_type == TransactionType.TRANSFER:
        validate_transfer(session, transaction_data)
        return

    validate_income_or_expense(session, transaction_data)


def validate_transfer(
    session: Session,
    transaction_data: TransactionCreate | TransactionUpdate,
) -> None:
    if transaction_data.target_account_id is None:
        raise TransactionValidationError("target_account_id is required for transfer transactions")

    target_account = account_repository.get_account(session, transaction_data.target_account_id)
    if target_account is None:
        raise TransactionValidationError("target_account_id does not reference an existing account")

    if transaction_data.account_id == transaction_data.target_account_id:
        raise TransactionValidationError("transfer source and target accounts must be different")


def validate_income_or_expense(
    session: Session,
    transaction_data: TransactionCreate | TransactionUpdate,
) -> None:
    if transaction_data.category_id is None:
        raise TransactionValidationError("category_id is required for income and expense transactions")

    category = category_repository.get_category(session, transaction_data.category_id)
    if category is None:
        raise TransactionValidationError("category_id does not reference an existing category")

    if transaction_data.transaction_type == TransactionType.INCOME and category.type != CategoryType.INCOME:
        raise TransactionValidationError("income transaction must use an income category")

    if transaction_data.transaction_type == TransactionType.EXPENSE and category.type != CategoryType.EXPENSE:
        raise TransactionValidationError("expense transaction must use an expense category")
