from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.database import get_session
from app.schemas.budget_schema import (
    BudgetCreate,
    BudgetMonthlySummary,
    BudgetRead,
    BudgetUpdate,
)
from app.services import budget_service
from app.services.budget_service import BudgetValidationError

router = APIRouter(prefix="/budgets", tags=["budgets"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[BudgetRead])
def list_budgets(session: SessionDependency) -> list[BudgetRead]:
    return budget_service.list_budgets(session)


@router.get("/monthly-summary", response_model=list[BudgetMonthlySummary])
def get_monthly_summary(
    year: int,
    month: int,
    session: SessionDependency,
) -> list[BudgetMonthlySummary]:
    try:
        return budget_service.get_monthly_summary(session, year, month)
    except BudgetValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, session: SessionDependency) -> BudgetRead:
    budget = budget_service.get_budget(session, budget_id)
    if budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    return budget


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(budget_create: BudgetCreate, session: SessionDependency) -> BudgetRead:
    try:
        return budget_service.create_budget(session, budget_create)
    except BudgetValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    session: SessionDependency,
) -> BudgetRead:
    try:
        budget = budget_service.update_budget(session, budget_id, budget_update)
    except BudgetValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, session: SessionDependency) -> Response:
    deleted = budget_service.delete_budget(session, budget_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
