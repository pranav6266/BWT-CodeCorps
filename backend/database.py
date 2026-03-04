import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError(
        "No MONGO_URI found in environment variables. Please check your .env file."
    )

client = AsyncIOMotorClient(MONGO_URI)

db = client.financial_assistant

users_collection = db.get_collection("users")
expenses_collection = db.get_collection("expenses")
decisions_collection = db.get_collection("decisions")
chat_messages_collection = db.get_collection("chat_messages")


async def create_indexes():
    """Create indexes for optimal query performance."""
    try:
        await users_collection.create_index("user_id", unique=True)
        await users_collection.create_index("clerk_user_id", unique=True)

        await expenses_collection.create_index("user_id")
        await expenses_collection.create_index([("user_id", 1), ("created_at", -1)])

        await decisions_collection.create_index("user_id")
        await decisions_collection.create_index([("user_id", 1), ("created_at", -1)])

        await chat_messages_collection.create_index("user_id")
        await chat_messages_collection.create_index([("user_id", 1), ("created_at", 1)])

        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")


async def ping_server():
    """Ping the database to confirm a successful connection."""
    try:
        await client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
