# backend/app/services/llm_layer_two.py

import json
import logging
from typing import Dict, Any
from ..models.system_prompt import get_second_system_prompt
from ..utils.request_pipeline_pro import add_request_to_queue_pro

logger = logging.getLogger(__name__)

async def validate_llm_one_response(page_id: str, llm_one_response: Dict[str, Any], client_name: str) -> Dict[str, Any]:
    try:
        logger.info(f"LLM Layer Two: Validating response for page {page_id}")
        second_system_prompt = get_second_system_prompt()

        # Prepare content for the second LLM
        second_content = [
            second_system_prompt,
            f"JSON Input:\n{json.dumps(llm_one_response)}"
        ]

        # Add the request to the pro queue and await the result
        future = add_request_to_queue_pro(second_content)
        second_response = await future

        second_response_text = second_response.text
        logger.info(f"LLM Layer Two: Raw response for page {page_id}: {second_response_text}")

        # Parse the second response JSON
        try:
            second_response_json = json.loads(second_response_text)
            logger.info(f"LLM Layer Two: Successfully validated page {page_id}")
            return {
                "page_id": page_id,
                "second_response": second_response_json
            }
        except json.JSONDecodeError as json_error:
            logger.error(f"LLM Layer Two: Invalid JSON response for page {page_id}. Error: {str(json_error)}")
            return {
                "page_id": page_id,
                "second_response": second_response_text,
                "error": f"Invalid JSON response from second LLM: {str(json_error)}"
            }

    except Exception as e:
        logger.error(f"LLM Layer Two: Error validating page {page_id}: {str(e)}")
        return {
            "page_id": page_id,
            "error": str(e)
        }
