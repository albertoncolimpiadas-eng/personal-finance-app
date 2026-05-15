from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session

from app.database import get_session
from app.models.transaction import TransactionType
from app.schemas.transaction_schema import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.services import transaction_service
from app.services.transaction_service import TransactionValidationError

router = APIRouter(prefix="/transactions", tags=["transactions"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    session: SessionDependency,
    account_id: int | None = None,
    category_id: int | None = None,
    transaction_type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    text: str | None = Query(default=None, description="Search in transaction description"),
) -> list[TransactionRead]:
    return transaction_service.list_transactions(
        session=session,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        date_from=date_from,
        date_to=date_to,
        text=text,
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, session: SessionDependency) -> TransactionRead:
    transaction = transaction_service.get_transaction(session, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_create: TransactionCreate,
    session: SessionDependency,
) -> TransactionRead:
    try:
        return transaction_service.create_transaction(session, transaction_create)
    except TransactionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    session: SessionDependency,
) -> TransactionRead:
    try:
        transaction = transaction_service.update_transaction(
            session,
            transaction_id,
            transaction_update,
        )
    except TransactionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, session: SessionDependency) -> Response:
    deleted = transaction_service.delete_transaction(session, transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
