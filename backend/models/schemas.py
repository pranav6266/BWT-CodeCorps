# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    category: str = Field(..., min_length=1, description="Expense category")
    title: Optional[str] = None
    description: Optional[str] = None


class DecisionRequest(BaseModel):
    decision_type: str = Field(
        ..., min_length=1, description="e.g., New EMI, Vehicle Loan, Medical Emergency"
    )
    amount: float = Field(..., gt=0, description="Decision amount (must be positive)")
    duration_months: Optional[int] = Field(
        None, gt=0, description="Duration in months (must be positive if provided)"
    )
    description: Optional[str] = None


class UserProfile(BaseModel):
    monthly_income: float = Field(
        ..., gt=0, description="User's total monthly income (must be positive)"
    )
    current_debt: float = Field(
        ...,
        ge=0,
        description="User's current total monthly debt obligations (must be non-negative)",
    )
    savings_rate: float = Field(
        ..., ge=0, le=100, description="Percentage of income saved monthly (0-100)"
    )


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="Chat message")
