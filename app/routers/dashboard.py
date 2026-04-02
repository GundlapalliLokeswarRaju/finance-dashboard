from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_analyst_or_above, require_any_role
from app.database import get_db
from app.models.user import User
from app.schemas.transaction import DashboardSummary
from app.services.dashboard import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Full dashboard summary [Analyst, Admin]",
)
def dashboard_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    """
    Returns aggregated financial data including:
    - Total income, expenses, and net balance
    - Category-wise totals
    - Monthly trends (income vs expense per month)
    - 10 most recent transactions
    """
    return get_dashboard_summary(db)
