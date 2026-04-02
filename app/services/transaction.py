from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionFilters, TransactionUpdate


def create_transaction(db: Session, payload: TransactionCreate, user_id: int) -> Transaction:
    tx = Transaction(**payload.model_dump(), created_by=user_id)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transaction_by_id(db: Session, tx_id: int) -> Transaction:
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == tx_id, Transaction.is_deleted == 0)
        .first()
    )
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {tx_id} not found",
        )
    return tx


def get_transactions(db: Session, filters: TransactionFilters) -> dict:
    query = db.query(Transaction).filter(Transaction.is_deleted == 0)

    if filters.type:
        query = query.filter(Transaction.type == filters.type)
    if filters.category:
        query = query.filter(Transaction.category.ilike(f"%{filters.category}%"))
    if filters.date_from:
        query = query.filter(Transaction.date >= filters.date_from)
    if filters.date_to:
        query = query.filter(Transaction.date <= filters.date_to)

    total = query.count()
    offset = (filters.page - 1) * filters.page_size
    transactions = (
        query.order_by(Transaction.date.desc())
        .offset(offset)
        .limit(filters.page_size)
        .all()
    )

    return {
        "total": total,
        "page": filters.page,
        "page_size": filters.page_size,
        "transactions": transactions,
    }


def update_transaction(db: Session, tx_id: int, payload: TransactionUpdate) -> Transaction:
    tx = get_transaction_by_id(db, tx_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


def soft_delete_transaction(db: Session, tx_id: int) -> None:
    tx = get_transaction_by_id(db, tx_id)
    tx.is_deleted = 1
    db.commit()
