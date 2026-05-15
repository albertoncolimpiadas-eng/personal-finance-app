import csv
from io import StringIO

from sqlmodel import Session

from app.repositories import account_repository, category_repository, transaction_repository


def export_transactions_csv(session: Session) -> str:
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "date",
            "description",
            "amount",
            "account_name",
            "category_name",
            "transaction_type",
        ],
    )
    writer.writeheader()
    for transaction in transaction_repository.list_transactions(session):
        account = account_repository.get_account(session, transaction.account_id)
        category = (
            category_repository.get_category(session, transaction.category_id)
            if transaction.category_id is not None
            else None
        )
        writer.writerow(
            {
                "date": transaction.date.isoformat(),
                "description": transaction.description,
                "amount": str(transaction.amount),
                "account_name": account.name if account else "",
                "category_name": category.name if category else "",
                "transaction_type": transaction.transaction_type.value,
            }
        )
    return output.getvalue()
