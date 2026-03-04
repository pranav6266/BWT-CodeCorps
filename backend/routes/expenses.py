from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ExpenseCreate
from utils.clerk_auth import get_current_user
from database import expenses_collection
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()


@router.post("", description="Add a new expense record")
async def create_expense(
    expense: ExpenseCreate, user_id: str = Depends(get_current_user)
):
    expense_dict = expense.model_dump()

    title = expense_dict.pop("title", None)
    description = expense_dict.get("description") or title

    expense_dict["description"] = description
    expense_dict["user_id"] = user_id
    expense_dict["created_at"] = datetime.now(timezone.utc)

    result = await expenses_collection.insert_one(expense_dict)

    return {
        "id": str(result.inserted_id),
        "title": title or description,
        "amount": expense.amount,
        "category": expense.category,
        "description": description,
        "message": "Expense added successfully",
    }


@router.get("", description="Retrieve user expenses")
async def get_expenses(user_id: str = Depends(get_current_user)):
    try:
        expenses_cursor = expenses_collection.find({"user_id": user_id})
        expenses = await expenses_cursor.to_list(length=100)

        for exp in expenses:
            exp["_id"] = str(exp["_id"])
        return expenses
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses")


@router.delete("/{id}", description="Delete a specific expense")
async def delete_expense(id: str, user_id: str = Depends(get_current_user)):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid expense ID format")

    try:
        result = await expenses_collection.delete_one(
            {"_id": object_id, "user_id": user_id}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Expense not found or unauthorized"
            )
        return {"message": "Expense deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting expense: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete expense")
