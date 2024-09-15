# backend/app/services/llm_layer_one.py

import json
import logging
from ..models.gemini_model import model
from ..models.system_prompt import get_system_prompt
from ..utils.request_pipeline import add_request_to_queue

logger = logging.getLogger(__name__)

async def analyze_page_with_llm_one(page, pdf_data, query, client_name):
    try:
        logger.info(f"LLM Layer One: Processing page {page['id']}")
        image_path = page['image_path']  # Assuming 'image_path' is part of the page data

        with open(image_path, 'rb') as img_file:
            img_byte_arr = img_file.read()

        system_prompt = get_system_prompt()
        content = [
            {
                "mime_type": "image/png",
                "data": img_byte_arr
            },
            f"""
            {system_prompt}
            Publication: {pdf_data['publication_name']}
            Edition: {pdf_data['edition']}
            Date: {pdf_data['date']}
            Page: {page['number']}
            
            Query: {query}
            """
        ]

        # Add the request to the queue and await the result
        future = add_request_to_queue(content)
        response = await future

        response_text = response.text
        logger.info(f"LLM Layer One: Successfully processed page {page['id']}")

        # Parse the response JSON
        try:
            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"LLM Layer One: Invalid JSON response for page {page['id']}")
            return {
                "page_id": page['id'],
                "first_response": response_text,
                "error": "Invalid JSON response from first LLM"
            }

        return {
            "page_id": page['id'],
            "first_response": response_json
        }

    except Exception as e:
        logger.error(f"LLM Layer One: Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page['id'],
            "error": str(e)
        }
