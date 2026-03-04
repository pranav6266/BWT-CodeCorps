from fastapi import APIRouter, Depends, HTTPException
from models.schemas import UserProfile
from utils.clerk_auth import get_current_user
from database import users_collection
from datetime import datetime, timezone

router = APIRouter()


@router.get("", description="Get the user's financial profile")
async def get_profile(user_id: str = Depends(get_current_user)):
    try:
        print(f"[Profile GET] Fetching profile for user_id: {user_id}")
        user = await users_collection.find_one({"user_id": user_id})
        print(f"[Profile GET] Found user in DB: {user is not None}")

        if not user:
            return {"monthlyIncome": "", "currentEmi": "", "targetSavingsRate": ""}

        return {
            "monthlyIncome": user.get("monthly_income", ""),
            "currentEmi": user.get("current_debt", ""),
            "targetSavingsRate": user.get("savings_rate", ""),
        }
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching profile"
        )


@router.post("", description="Update the user's financial profile")
async def update_profile(
    profile: UserProfile, user_id: str = Depends(get_current_user)
):
    try:
        print(f"[Profile POST] Saving profile for user_id: {user_id}")
        print(f"[Profile POST] Profile data: {profile.model_dump()}")

        profile_data = {
            "monthly_income": profile.monthly_income,
            "current_debt": profile.current_debt,
            "savings_rate": profile.savings_rate,
            "user_id": user_id,
            "clerk_user_id": user_id,
            "updated_at": datetime.now(timezone.utc),
        }

        result = await users_collection.update_one(
            {"user_id": user_id}, {"$set": profile_data}, upsert=True
        )
        print(f"[Profile POST] Upsert result: {result.acknowledged}")

        return {
            "monthlyIncome": profile.monthly_income,
            "currentEmi": profile.current_debt,
            "targetSavingsRate": profile.savings_rate,
        }
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while updating profile"
        )
