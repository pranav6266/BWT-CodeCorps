from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import ping_server, create_indexes
from routes import expenses, decision, chat, profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up FastAPI server...")
    await ping_server()
    await create_indexes()
    yield
    print("Shutting down FastAPI server...")


app = FastAPI(
    title="AI-Powered Financial Safety & Decision Assistant",
    description="Backend API for tracking expenses and evaluating financial decisions.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(decision.router, tags=["Decisions"])
app.include_router(chat.router, prefix="/chat", tags=["AI Chat"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Financial Assistant API.",
        "status": "Server is running successfully.",
    }
