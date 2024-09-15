# backend/app/services/llm_layer_two.py

import json
import logging
from models.gemini_model import model  # Ensure this path is correct
from models.system_prompt import get_second_system_prompt
from utils.request_pipeline import add_request_to_queue
from utils.general_utils import load_clients  # Correct import

logger = logging.getLogger(__name__)

async def validate_llm_one_response(page_id, llm_one_response, client_name):
    try:
        logger.info(f"LLM Layer Two: Validating response for page {page_id}")
        second_system_prompt = get_second_system_prompt()

        clients = load_clients()
        client_data = clients.get(client_name, {})
        client_background = client_data.get("details", "No background provided.")

        # Format the second system prompt with client details
        second_system_prompt_formatted = second_system_prompt.format(
            client_name=client_name,
            client_background=client_background
        )

        # Prepare content for the second LLM
        second_content = [
            second_system_prompt_formatted,
            f"JSON Input:\n{json.dumps(llm_one_response)}"
        ]

        # Add the request to the queue and await the result
        future = add_request_to_queue(second_content)
        second_response = await future

        second_response_text = second_response.text
        logger.info(f"LLM Layer Two: Successfully validated page {page_id}")

        # Parse the second response JSON
        try:
            second_response_json = json.loads(second_response_text)
        except json.JSONDecodeError:
            logger.error(f"LLM Layer Two: Invalid JSON response for page {page_id}")
            return {
                "page_id": page_id,
                "second_response": second_response_text,
                "error": "Invalid JSON response from second LLM"
            }

        return {
            "page_id": page_id,
            "second_response": second_response_json
        }

    except Exception as e:
        logger.error(f"LLM Layer Two: Error validating page {page_id}: {str(e)}")
        return {
            "page_id": page_id,
            "error": str(e)
        }