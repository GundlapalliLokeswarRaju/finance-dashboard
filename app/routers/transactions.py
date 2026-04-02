from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, require_analyst_or_above, require_any_role
from app.database import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilters,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from app.services import transaction as tx_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=201,
    summary="Create a transaction [Admin only]",
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return tx_service.create_transaction(db, payload, current_user.id)


@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="List transactions with filters [Analyst, Admin]",
)
def list_transactions(
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    category: Optional[str] = Query(None, description="Filter by category (partial match)"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    filters = TransactionFilters(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return tx_service.get_transactions(db, filters)


@router.get(
    "/{tx_id}",
    response_model=TransactionResponse,
    summary="Get a single transaction [Analyst, Admin]",
)
def get_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    return tx_service.get_transaction_by_id(db, tx_id)


@router.patch(
    "/{tx_id}",
    response_model=TransactionResponse,
    summary="Update a transaction [Admin only]",
)
def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return tx_service.update_transaction(db, tx_id, payload)


@router.delete(
    "/{tx_id}",
    status_code=204,
    summary="Soft-delete a transaction [Admin only]",
)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    tx_service.soft_delete_transaction(db, tx_id)
