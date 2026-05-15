from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.schemas.dashboard_schema import DashboardMonthlySummary, DashboardYearlyMonthSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("/monthly-summary", response_model=DashboardMonthlySummary)
def get_monthly_summary(
    year: int,
    month: int,
    session: SessionDependency,
) -> DashboardMonthlySummary:
    try:
        return dashboard_service.get_monthly_summary(session, year, month)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/yearly-summary", response_model=list[DashboardYearlyMonthSummary])
def get_yearly_summary(
    year: int,
    session: SessionDependency,
) -> list[DashboardYearlyMonthSummary]:
    try:
        return dashboard_service.get_yearly_summary(session, year)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
