# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None

class DecisionRequest(BaseModel):
    decision_type: str = Field(..., description="e.g., New EMI, Vehicle Loan, Medical Emergency")
    amount: float
    duration_months: Optional[int] = None
    description: Optional[str] = None

class UserProfile(BaseModel):
    monthly_income: float = Field(..., description="User's total monthly income")
    current_debt: float = Field(..., description="User's current total monthly debt obligations")
    savings_rate: float = Field(..., description="Percentage of income saved monthly")
    
class ChatRequest(BaseModel):
    message: str