from fastapi import APIRouter, Depends, HTTPException
from models.schemas import DecisionRequest
from utils.clerk_auth import get_current_user
from database import decisions_collection, users_collection, expenses_collection
from services.metrics_engine import evaluate_decision_risk
from services.ai_service import evaluate_decision_explanation
from datetime import datetime, timezone

router = APIRouter()


@router.post("/evaluate-decision", description="Evaluate risk of a financial decision")
async def evaluate_decision(
    request: DecisionRequest, user_id: str = Depends(get_current_user)
):
    try:
        user_profile = await users_collection.find_one({"user_id": user_id})
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")

    if not user_profile or user_profile.get("monthly_income", 0) <= 0:
        return {
            "warning": True,
            "message": "Please set up your financial profile in the Dashboard first with a valid monthly income before evaluating decisions.",
            "risk_level": "Unknown",
            "metrics_at_evaluation": {
                "monthly_income": 0,
                "projected_dti_percentage": 0,
                "current_savings_rate": 0,
            },
            "ai_explanation": "We couldn't evaluate your decision because we don't have your financial profile. Please go to the Dashboard and enter your monthly income, current EMI/debt, and target savings rate. Once we have this information, we can provide you with accurate risk assessments.",
        }

    user_income = user_profile.get("monthly_income", 0.0)
    current_debt = user_profile.get("current_debt", 0.0)
    savings_rate = user_profile.get("savings_rate", 0.0)

    try:
        expenses_cursor = expenses_collection.find({"user_id": user_id})
        expenses = await expenses_cursor.to_list(length=1000)
        total_monthly_expenses = sum(exp.get("amount", 0) for exp in expenses)
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        total_monthly_expenses = 0

    if request.duration_months and request.duration_months > 0:
        new_emi = request.amount / request.duration_months
    else:
        new_emi = request.amount

    evaluation = evaluate_decision_risk(
        monthly_income=user_income,
        current_monthly_debt=current_debt,
        new_monthly_obligation=new_emi,
        savings_rate=savings_rate,
        current_total_expenses=total_monthly_expenses,
    )

    metrics_context = {
        "monthly_income": user_income,
        "projected_dti_percentage": evaluation["projected_dti"],
        "current_savings_rate": savings_rate,
        "risk_score": evaluation.get("risk_score", 0),
    }

    ai_explanation = await evaluate_decision_explanation(
        decision_data=request.model_dump(),
        risk_level=evaluation["risk_level"],
        metrics=metrics_context,
    )

    decision_record = {
        "user_id": user_id,
        "decision": request.model_dump(),
        "metrics_at_evaluation": metrics_context,
        "risk_level": evaluation["risk_level"],
        "risk_score": evaluation.get("risk_score", 0),
        "risk_factors": evaluation.get("risk_factors", []),
        "warnings": evaluation.get("warnings", []),
        "ai_explanation": ai_explanation,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = await decisions_collection.insert_one(decision_record)
        decision_record["_id"] = str(result.inserted_id)
    except Exception as e:
        print(f"Error saving decision: {e}")
        decision_record["_id"] = None

    return decision_record
