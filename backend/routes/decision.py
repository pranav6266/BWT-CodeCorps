from fastapi import APIRouter, Depends, HTTPException
from models.schemas import DecisionRequest
from utils.clerk_auth import get_current_user
from database import decisions_collection, users_collection  # Added users_collection
from services.metrics_engine import evaluate_decision_risk
from services.ai_service import evaluate_decision_explanation
from datetime import datetime, timezone

router = APIRouter()


@router.post("/evaluate-decision", description="Evaluate risk of a financial decision")
async def evaluate_decision(request: DecisionRequest, user_id: str = Depends(get_current_user)):
    # 1. Fetch REAL user profile
    user_profile = await users_collection.find_one({"user_id": user_id})

    if not user_profile or user_profile.get("monthly_income", 0) <= 0:
        raise HTTPException(status_code=400, detail="Please set up your financial profile in the Dashboard first.")

    user_income = user_profile.get("monthly_income", 0.0)
    current_debt = user_profile.get("current_debt", 0.0)
    savings_rate = user_profile.get("savings_rate", 0.0)

    # 2. Calculate the deterministic risk based on the requested new EMI amount
    new_emi = request.amount / request.duration_months if request.duration_months else request.amount

    evaluation = evaluate_decision_risk(
        monthly_income=user_income,
        current_monthly_debt=current_debt,
        new_monthly_obligation=new_emi,
        savings_rate=savings_rate
    )

    # 3. Ask the AI to explain this specific risk level contextually
    metrics_context = {
        "monthly_income": user_income,
        "projected_dti_percentage": evaluation["projected_dti"],
        "current_savings_rate": savings_rate
    }

    ai_explanation = await evaluate_decision_explanation(
        decision_data=request.model_dump(),
        risk_level=evaluation["risk_level"],
        metrics=metrics_context
    )

    # 4. Save the full record to the database
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