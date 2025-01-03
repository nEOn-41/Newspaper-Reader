import google.generativeai as genai
from ..config import GEMINI_API_KEY
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create the model
generation_config: Dict[str, Any] = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

def get_gemini_model() -> genai.GenerativeModel:
    """
    Returns the configured Gemini model instance.

    Returns:
        genai.GenerativeModel: The configured Gemini model instance.
    """
    return model