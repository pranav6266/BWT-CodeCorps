from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ChatRequest
from utils.clerk_auth import get_current_user
from database import chat_messages_collection, users_collection, expenses_collection
from services.ai_service import generate_chat_response
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", description="Send a message to the AI assistant")
async def send_message(request: ChatRequest, user_id: str = Depends(get_current_user)):
    try:
        user_msg = {
            "user_id": user_id,
            "role": "user",
            "content": request.message,
            "created_at": datetime.now(timezone.utc),
        }
        await chat_messages_collection.insert_one(user_msg)
    except Exception as e:
        print(f"Error saving user message: {e}")
        raise HTTPException(status_code=500, detail="Failed to save message")

    try:
        user_profile = await users_collection.find_one({"user_id": user_id}) or {}
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        user_profile = {}

    try:
        expenses_cursor = expenses_collection.find({"user_id": user_id})
        expenses = await expenses_cursor.to_list(length=1000)
        total_expenses = sum(exp.get("amount", 0) for exp in expenses)
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        total_expenses = 0

    real_financial_context = (
        f"Monthly income: ₹{user_profile.get('monthly_income', 0)}, "
        f"Total Monthly Expenses logged: ₹{total_expenses}, "
        f"Current Monthly Debt: ₹{user_profile.get('current_debt', 0)}, "
        f"Savings Rate: {user_profile.get('savings_rate', 0)}%"
    )

    try:
        ai_reply_text = await generate_chat_response(
            user_message=request.message, user_context=real_financial_context
        )
    except Exception as e:
        print(f"Error generating AI response: {e}")
        raise HTTPException(status_code=503, detail="AI service unavailable")

    try:
        ai_msg = {
            "user_id": user_id,
            "role": "assistant",
            "content": ai_reply_text,
            "created_at": datetime.now(timezone.utc),
        }
        await chat_messages_collection.insert_one(ai_msg)
    except Exception as e:
        print(f"Error saving AI response: {e}")

    return {"reply": ai_reply_text}


@router.get("/chat-history", description="Retrieve conversation history")
async def get_chat_history(user_id: str = Depends(get_current_user)):
    try:
        messages = (
            await chat_messages_collection.find({"user_id": user_id})
            .sort("created_at", 1)
            .to_list(length=100)
        )
        for msg in messages:
            msg["_id"] = str(msg["_id"])
        return messages
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")
