from fastapi import APIRouter, Depends
from models.schemas import DecisionRequest
from utils.clerk_auth import get_current_user
from database import decisions_collection
from services.metrics_engine import evaluate_decision_risk
from services.ai_service import evaluate_decision_explanation
from datetime import datetime, timezone

router = APIRouter()


@router.post("/evaluate-decision", description="Evaluate risk of a financial decision")
async def evaluate_decision(request: DecisionRequest, user_id: str = Depends(get_current_user)):
    # In a fully finished app, you would fetch these from the 'users' and 'expenses' collections
    # For now, we are mocking the user's current baseline profile
    mock_user_income = 15000.0
    mock_current_debt = 2000.0
    mock_savings_rate = 8.0

    # 1. Calculate the deterministic risk based on the requested new EMI amount
    new_emi = request.amount / request.duration_months if request.duration_months else request.amount

    evaluation = evaluate_decision_risk(
        monthly_income=mock_user_income,
        current_monthly_debt=mock_current_debt,
        new_monthly_obligation=new_emi,
        savings_rate=mock_savings_rate
    )

    # 2. Ask the AI to explain this specific risk level contextually
    metrics_context = {
        "monthly_income": mock_user_income,
        "projected_dti_percentage": evaluation["projected_dti"],
        "current_savings_rate": mock_savings_rate
    }

    ai_explanation = await evaluate_decision_explanation(
        decision_data=request.model_dump(),
        risk_level=evaluation["risk_level"],
        metrics=metrics_context
    )

    # 3. Save the full record to the database
    decision_record = {
        "user_id": user_id,
        "decision": request.model_dump(),
        "metrics_at_evaluation": metrics_context,
        "risk_level": evaluation["risk_level"],
        "ai_explanation": ai_explanation,
        "created_at": datetime.now(timezone.utc)
    }

    result = await decisions_collection.insert_one(decision_record)
    decision_record["_id"] = str(result.inserted_id)

    return decision_record