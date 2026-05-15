from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.database import get_session
from app.schemas.account_schema import (
    AccountBalance,
    AccountCreate,
    AccountRead,
    AccountSummary,
    AccountUpdate,
)
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[AccountRead])
def list_accounts(session: SessionDependency) -> list[AccountRead]:
    return account_service.list_accounts(session)


@router.get("/summary", response_model=list[AccountSummary])
def list_account_summaries(session: SessionDependency) -> list[AccountSummary]:
    return account_service.list_account_summaries(session)


@router.get("/{account_id}/balance", response_model=AccountBalance)
def get_account_balance(account_id: int, session: SessionDependency) -> AccountBalance:
    account_balance = account_service.get_account_balance(session, account_id)
    if account_balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return account_balance


@router.get("/{account_id}", response_model=AccountRead)
def get_account(account_id: int, session: SessionDependency) -> AccountRead:
    account = account_service.get_account(session, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return account


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(
    account_create: AccountCreate,
    session: SessionDependency,
) -> AccountRead:
    return account_service.create_account(session, account_create)


@router.put("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    session: SessionDependency,
) -> AccountRead:
    account = account_service.update_account(session, account_id, account_update)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, session: SessionDependency) -> Response:
    deleted = account_service.delete_account(session, account_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
