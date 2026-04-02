from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import CategoryTotal, DashboardSummary, MonthlyTrend


def get_dashboard_summary(db: Session) -> DashboardSummary:
    active_txs = db.query(Transaction).filter(Transaction.is_deleted == 0)

    # ── Totals ───────────────────────────────────────────────────────────────
    income_row = (
        active_txs.filter(Transaction.type == TransactionType.income)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )
    expense_row = (
        active_txs.filter(Transaction.type == TransactionType.expense)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    total_income = round(float(income_row), 2)
    total_expenses = round(float(expense_row), 2)
    net_balance = round(total_income - total_expenses, 2)
    total_transactions = active_txs.count()

    # ── Category totals ──────────────────────────────────────────────────────
    cat_rows = (
        active_txs
        .with_entities(Transaction.category, func.sum(Transaction.amount))
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    category_totals = [
        CategoryTotal(category=row[0], total=round(float(row[1]), 2))
        for row in cat_rows
    ]

    # ── Monthly trends ───────────────────────────────────────────────────────
    # Group all transactions by year-month
    all_txs = active_txs.with_entities(
        Transaction.date, Transaction.type, Transaction.amount
    ).all()

    monthly: dict[str, dict] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for tx_date, tx_type, tx_amount in all_txs:
        key = tx_date.strftime("%Y-%m")
        monthly[key][tx_type.value] += float(tx_amount)

    monthly_trends = [
        MonthlyTrend(
            month=month,
            income=round(data["income"], 2),
            expense=round(data["expense"], 2),
            net=round(data["income"] - data["expense"], 2),
        )
        for month, data in sorted(monthly.items())
    ]

    # ── Recent transactions (last 10) ────────────────────────────────────────
    recent = (
        active_txs.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    return DashboardSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        total_transactions=total_transactions,
        category_totals=category_totals,
        monthly_trends=monthly_trends,
        recent_transactions=recent,
    )
