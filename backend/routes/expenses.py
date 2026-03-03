from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ExpenseCreate
from utils.clerk_auth import get_current_user
from database import expenses_collection
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", description="Add a new expense record")
async def create_expense(expense: ExpenseCreate, user_id: str = Depends(get_current_user)):
    expense_dict = expense.model_dump()
    expense_dict["user_id"] = user_id
    expense_dict["created_at"] = datetime.now(timezone.utc)

    result = await expenses_collection.insert_one(expense_dict)
    return {"id": str(result.inserted_id), "message": "Expense added successfully"}


@router.get("/", description="Retrieve user expenses")
async def get_expenses(user_id: str = Depends(get_current_user)):
    expenses_cursor = expenses_collection.find({"user_id": user_id})
    expenses = await expenses_cursor.to_list(length=100)

    # Convert MongoDB ObjectIds to strings for JSON serialization
    for exp in expenses:
        exp["_id"] = str(exp["_id"])
    return expenses


@router.delete("/{id}", description="Delete a specific expense")
async def delete_expense(id: str, user_id: str = Depends(get_current_user)):
    result = await expenses_collection.delete_one({"_id": ObjectId(id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found or unauthorized")
    return {"message": "Expense deleted successfully"}