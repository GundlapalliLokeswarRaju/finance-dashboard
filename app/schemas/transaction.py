from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionType


# ── Auth schemas ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Transaction request schemas ──────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip()


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v else v


# ── Transaction filter schema ────────────────────────────────────────────────

class TransactionFilters(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20

    @field_validator("page_size")
    @classmethod
    def limit_page_size(cls, v: int) -> int:
        if v > 100:
            raise ValueError("page_size cannot exceed 100")
        return v


# ── Transaction response schemas ─────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str]
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    transactions: list[TransactionResponse]


# ── Dashboard schemas ────────────────────────────────────────────────────────

class CategoryTotal(BaseModel):
    category: str
    total: float


class MonthlyTrend(BaseModel):
    month: str          # e.g. "2024-03"
    income: float
    expense: float
    net: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_transactions: int
    category_totals: list[CategoryTotal]
    monthly_trends: list[MonthlyTrend]
    recent_transactions: list[TransactionResponse]
