import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. AI features will not work.")
else:
    # Configure the Gemini SDK with your API key
    genai.configure(api_key=GEMINI_API_KEY)

# Core system prompt to enforce the AI's constraints
SYSTEM_PROMPT = """You are an AI Financial Stability Companion designed to assist low-income households (e.g., ~₹15,000 monthly income) in making safer financial decisions. 
Your role is strictly to interpret data. You must provide contextual explanations for risks that are strictly grounded in the user's specific financial data without relying on external assumptions.
Keep your language accessible, empathetic, responsible, and easy to understand."""

# Initialize the Gemini model with the system instructions
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",  # Google's fast and cost-effective model
    system_instruction=SYSTEM_PROMPT
)


async def generate_chat_response(user_message: str, user_context: str = "No prior financial context provided.") -> str:
    """
    Sends a message to Gemini to get a conversational response,
    grounded in the user's current financial state.
    """
    # Combine the context and the user's message into a single prompt
    prompt = f"User's current financial context: {user_context}\n\nUser Message: {user_message}"

    try:
        # Gemini's async generation method
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.2)
        )
        return response.text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return "I am currently experiencing connection issues. Please try again later."


async def evaluate_decision_explanation(decision_data: dict, risk_level: str, metrics: dict) -> str:
    """
    Generates a targeted explanation for why a specific financial decision
    was given a certain risk level.
    """
    prompt = f"""
    The user is considering the following financial decision:
    Decision Details: {decision_data}

    Our deterministic backend calculated the following:
    Current User Metrics: {metrics}
    Resulting Risk Level: {risk_level}

    Provide a short, 2-3 sentence explanation to the user explaining *why* this decision is considered '{risk_level}'. Base your explanation entirely on how the decision impacts their specific metrics.
    """

    try:
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.2)
        )
        return response.text
    except Exception as e:
        print(f"Error generating decision explanation: {e}")
        return f"This decision carries a {risk_level} risk level based on your current metrics."