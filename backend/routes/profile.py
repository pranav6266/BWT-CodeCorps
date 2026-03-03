from fastapi import APIRouter, Depends, HTTPException
from models.schemas import UserProfile
from utils.clerk_auth import get_current_user
from database import users_collection
from datetime import datetime, timezone

router = APIRouter()


# Notice the empty string "" instead of "/"
@router.post("", description="Update the user's financial profile")
async def update_profile(profile: UserProfile, user_id: str = Depends(get_current_user)):
    try:
        profile_data = profile.model_dump()

        # Save both keys to satisfy MongoDB indexes and our other routes
        profile_data["user_id"] = user_id
        profile_data["clerk_user_id"] = user_id  # <-- This fixes the E11000 error
        profile_data["updated_at"] = datetime.now(timezone.utc)

        # Upsert: Update if exists, insert if it doesn't
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        return {"message": "Profile updated successfully"}
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while updating profile")


@router.post("", description="Update the user's financial profile")
async def update_profile(profile: UserProfile, user_id: str = Depends(get_current_user)):
    try:
        profile_data = profile.model_dump()
        profile_data["user_id"] = user_id  # Explicitly save the Clerk User ID
        profile_data["updated_at"] = datetime.now(timezone.utc)

        # Upsert: Update if exists, insert if it doesn't
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        return {"message": "Profile updated successfully"}
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while updating profile")