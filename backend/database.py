import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("No MONGO_URI found in environment variables. Please check your .env file.")

# Initialize the async MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Select the database (creating it if it doesn't exist)
db = client.financial_assistant

# Define collections based on the system architecture
users_collection = db.get_collection("users")
expenses_collection = db.get_collection("expenses")
decisions_collection = db.get_collection("decisions")
chat_messages_collection = db.get_collection("chat_messages")

async def ping_server():
    """Ping the database to confirm a successful connection."""
    try:
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")