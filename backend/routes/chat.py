from fastapi import APIRouter, Depends
from models.schemas import ChatRequest
from utils.clerk_auth import get_current_user
from database import chat_messages_collection, users_collection, expenses_collection  # Added collections
from services.ai_service import generate_chat_response
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", description="Send a message to the AI assistant")
async def send_message(request: ChatRequest, user_id: str = Depends(get_current_user)):
    # 1. Save the user's message to the database
    user_msg = {
        "user_id": user_id,
        "role": "user",
        "content": request.message,
        "created_at": datetime.now(timezone.utc)
    }
    await chat_messages_collection.insert_one(user_msg)

    # 2. Fetch REAL user profile and calculate total expenses
    user_profile = await users_collection.find_one({"user_id": user_id}) or {}

    # Calculate total expenses from the database
    expenses_cursor = expenses_collection.find({"user_id": user_id})
    expenses = await expenses_cursor.to_list(length=1000)
    total_expenses = sum(exp.get("amount", 0) for exp in expenses)

    # Build the real context for Gemini
    real_financial_context = (
        f"Monthly income: ₹{user_profile.get('monthly_income', 0)}, "
        f"Total Monthly Expenses logged: ₹{total_expenses}, "
        f"Current Monthly Debt: ₹{user_profile.get('current_debt', 0)}, "
        f"Savings Rate: {user_profile.get('savings_rate', 0)}%"
    )

    # 3. Call Grok (Gemini) to get the AI response
    ai_reply_text = await generate_chat_response(
        user_message=request.message,
        user_context=real_financial_context
    )

    # 4. Save Gemini's response to the database
    ai_msg = {
        "user_id": user_id,
        "role": "assistant",
        "content": ai_reply_text,
        "created_at": datetime.now(timezone.utc)
    }
    await chat_messages_collection.insert_one(ai_msg)

    return {"reply": ai_reply_text}
@router.get("/chat-history", description="Retrieve conversation history")
async def get_chat_history(user_id: str = Depends(get_current_user)):
    messages = await chat_messages_collection.find({"user_id": user_id}).sort("created_at", 1).to_list(length=100)
    # Convert MongoDB ObjectIds to strings for JSON serialization
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    return messages