import os
import asyncio
import google.generativeai as genai
from google.api_core.exceptions import (
    ServiceUnavailable,
    ResourceExhausted,
    DeadlineExceeded,
    InternalServerError,
)
from google.auth.exceptions import TransportError
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. AI features will not work.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are an AI Financial Stability Companion designed to assist low-income households (e.g., ~₹15,000 monthly income) in making safer financial decisions. 
Your role is strictly to interpret data. You must provide contextual explanations for risks that are strictly grounded in the user's specific financial data without relying on external assumptions.
Keep your language accessible, empathetic, responsible, and easy to understand."""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", system_instruction=SYSTEM_PROMPT
)

DEFAULT_TIMEOUT = 30.0


async def generate_chat_response(
    user_message: str,
    user_context: str = "No prior financial context provided.",
    max_retries: int = 3,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    prompt = f"User's current financial context: {user_context}\n\nUser Message: {user_message}"

    last_error = "Unknown error"

    for attempt in range(max_retries):
        try:
            response = await asyncio.wait_for(
                model.generate_content_async(
                    prompt, generation_config=genai.GenerationConfig(temperature=0.2)
                ),
                timeout=timeout,
            )
            return response.text
        except asyncio.TimeoutError:
            last_error = "Request timed out. Please try again."
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Request timed out, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except ResourceExhausted:
            last_error = "API rate limit exceeded"
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"Rate limited, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except (ServiceUnavailable, InternalServerError):
            last_error = "Gemini service is temporarily unavailable"
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"Service unavailable, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except TransportError as e:
            last_error = f"Connection error: Unable to reach AI service"
            print(f"Transport error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                await asyncio.sleep(wait_time)
                continue
        except DeadlineExceeded:
            last_error = "Request took too long. Please try again."
            print(f"Deadline exceeded on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                await asyncio.sleep(wait_time)
                continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            print(f"Error communicating with Gemini API: {e}")
            break

    return f"I apologize, but I'm having trouble connecting right now. {last_error} Please try again in a moment."


async def evaluate_decision_explanation(
    decision_data: dict,
    risk_level: str,
    metrics: dict,
    max_retries: int = 3,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    prompt = f"""
    The user is considering the following financial decision:
    Decision Details: {decision_data}

    Our deterministic backend calculated the following:
    Current User Metrics: {metrics}
    Resulting Risk Level: {risk_level}

    Provide a short, 2-3 sentence explanation to the user explaining *why* this decision is considered '{risk_level}'. Base your explanation entirely on how the decision impacts their specific metrics.
    """

    last_error = "Unknown error"

    for attempt in range(max_retries):
        try:
            response = await asyncio.wait_for(
                model.generate_content_async(
                    prompt, generation_config=genai.GenerationConfig(temperature=0.2)
                ),
                timeout=timeout,
            )
            return response.text
        except asyncio.TimeoutError:
            last_error = "Request timed out"
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Request timed out, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except ResourceExhausted:
            last_error = "API rate limit exceeded"
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"Rate limited, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except (ServiceUnavailable, InternalServerError):
            last_error = "Gemini service is temporarily unavailable"
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                print(f"Service unavailable, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
        except TransportError as e:
            last_error = "Connection error"
            print(f"Transport error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                await asyncio.sleep(wait_time)
                continue
        except DeadlineExceeded:
            last_error = "Request took too long"
            if attempt < max_retries - 1:
                wait_time = 2 ** (attempt + 1)
                await asyncio.sleep(wait_time)
                continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            print(f"Error generating decision explanation: {e}")
            break

    return f"This decision carries a {risk_level} risk level based on your current metrics. (AI explanation unavailable: {last_error})"
