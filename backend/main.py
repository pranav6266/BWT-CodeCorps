from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import ping_server
from routes import expenses, decision, chat


# Import routers once you create them in the 'routes' folder
# from routes import expenses, decision, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ping the database
    print("Starting up FastAPI server...")
    await ping_server()
    yield
    # Shutdown logic (if any)
    print("Shutting down FastAPI server...")

# Initialize FastAPI application
app = FastAPI(
    title="AI-Powered Financial Safety & Decision Assistant",
    description="Backend API for tracking expenses and evaluating financial decisions.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. For production, restrict this to your frontend URL.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Placeholder for routing (endpoints mapping to expenses, decisions, and chat)
app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(decision.router, tags=["Decisions"])
app.include_router(chat.router, tags=["AI Chat"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Financial Assistant API.",
        "status": "Server is running successfully."
    }