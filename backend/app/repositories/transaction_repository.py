from datetime import date

from sqlmodel import Session, col, or_, select

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction_schema import TransactionCreate, TransactionUpdate


def list_transactions(
    session: Session,
    account_id: int | None = None,
    category_id: int | None = None,
    transaction_type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    text: str | None = None,
) -> list[Transaction]:
    statement = select(Transaction)

    if account_id is not None:
        statement = statement.where(Transaction.account_id == account_id)
    if category_id is not None:
        statement = statement.where(Transaction.category_id == category_id)
    if transaction_type is not None:
        statement = statement.where(Transaction.transaction_type == transaction_type)
    if date_from is not None:
        statement = statement.where(Transaction.date >= date_from)
    if date_to is not None:
        statement = statement.where(Transaction.date <= date_to)
    if text:
        statement = statement.where(col(Transaction.description).ilike(f"%{text}%"))

    statement = statement.order_by(Transaction.date.desc(), Transaction.id.desc())
    return list(session.exec(statement).all())


def get_transaction(session: Session, transaction_id: int) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def list_transactions_for_account_balance(
    session: Session,
    account_id: int,
) -> list[Transaction]:
    statement = select(Transaction).where(
        or_(
            Transaction.account_id == account_id,
            Transaction.target_account_id == account_id,
        )
    )
    return list(session.exec(statement).all())


def create_transaction(
    session: Session,
    transaction_create: TransactionCreate,
) -> Transaction:
    transaction = Transaction.model_validate(transaction_create)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def update_transaction(
    session: Session,
    transaction: Transaction,
    transaction_update: TransactionUpdate,
) -> Transaction:
    transaction_data = transaction_update.model_dump()
    for field, value in transaction_data.items():
        setattr(transaction, field, value)

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def delete_transaction(session: Session, transaction: Transaction) -> None:
    session.delete(transaction)
    session.commit()
