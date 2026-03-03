from fastapi import APIRouter, Depends
from models.schemas import ChatRequest
from utils.clerk_auth import get_current_user
from database import chat_messages_collection
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

    # 2. Call Grok to get the AI response
    # (In the future, we will fetch the user's actual income/expenses from the DB here)
    mock_financial_context = "Monthly income: 15000, Total Expenses: 12000"

    ai_reply_text = await generate_chat_response(
        user_message=request.message,
        user_context=mock_financial_context
    )

    # 3. Save Grok's response to the database
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