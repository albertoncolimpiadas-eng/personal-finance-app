from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.database import get_session
from app.services.export_service import export_transactions_csv

router = APIRouter(prefix="/exports", tags=["exports"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get(
    "/transactions.csv",
    response_class=Response,
    summary="Export transactions as CSV",
)
def export_transactions(session: SessionDependency) -> Response:
    csv_content = export_transactions_csv(session)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="transactions.csv"'},
    )
