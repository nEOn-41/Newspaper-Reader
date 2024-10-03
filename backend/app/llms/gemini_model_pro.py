# backend/app/models/gemini_model_pro.py

import google.generativeai as genai
from ..config import GEMINI_API_KEY
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create the model for gemini-1.5-pro-latest
generation_config_pro: Dict[str, Any] = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model_pro = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config_pro,
)

def get_gemini_model_pro() -> genai.GenerativeModel:
    """
    Returns the configured Gemini Pro model instance.
    """
    return model_pro
