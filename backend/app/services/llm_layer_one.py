import json
import logging
import os
from typing import Dict, Any
from ..models.system_prompt import get_system_prompt
from ..utils.request_pipeline import add_request_to_queue

logger = logging.getLogger(__name__)

async def analyze_page_with_llm_one(page: Dict[str, Any], pdf_data: Dict[str, Any], query: str, client_name: str) -> Dict[str, Any]:
    """
    Analyzes a single page using the first LLM layer.

    This function processes a page image using the Gemini model, applying the system prompt
    and the given query to extract relevant information.

    Args:
        page (Dict[str, Any]): Dictionary containing page information, including the image path.
        pdf_data (Dict[str, Any]): Metadata about the PDF containing the page.
        query (str): The query to be applied to the page.
        client_name (str): The name of the client for whom the analysis is being performed.

    Returns:
        Dict[str, Any]: A dictionary containing the analysis results or error information.

    Raises:
        Exception: If there's an error during the analysis process.
    """
    try:
        logger.info(f"LLM Layer One: Processing page {page['id']}")
        image_path = page['image_path']

        if not os.path.exists(image_path):
            logger.error(f"LLM Layer One: Image file not found: {image_path}")
            return {
                "page_id": page['id'],
                "error": f"Image file not found: {image_path}"
            }

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
            Publication: {pdf_data.get('publication_name', 'Unknown')}
            Edition: {pdf_data.get('edition', 'Unknown')}
            Date: {pdf_data.get('date', 'Unknown')}
            Page: {page['number']}
            
            Query: {query}
            """
        ]

        # Import the model here to avoid circular imports
        from ..models.gemini_model import model

        # Add the request to the queue and await the result
        future = add_request_to_queue(content)
        response = await future

        try:
            response_text = response.text
        except AttributeError:
            logger.error(f"LLM Layer One: Invalid response for page {page['id']}. Response: {response}")
            return {
                "page_id": page['id'],
                "error": "Invalid response from LLM Layer One"
            }

        logger.info(f"LLM Layer One: Successfully processed page {page['id']}")

        # Parse the response JSON
        try:
            response_json = json.loads(response_text)
            
            # Filter out keywords with empty article arrays
            if "keywords" in response_json:
                response_json["keywords"] = [
                    keyword for keyword in response_json["keywords"]
                    if keyword.get("articles") and len(keyword["articles"]) > 0
                ]
            
            # If all keywords were filtered out, set retrieval to false
            if not response_json.get("keywords"):
                response_json["retrieval"] = False

            return {
                "page_id": page['id'],
                "first_response": response_json
            }

        except json.JSONDecodeError:
            logger.error(f"LLM Layer One: Invalid JSON response for page {page['id']}")
            return {
                "page_id": page['id'],
                "first_response": response_text,
                "error": "Invalid JSON response from first LLM"
            }

    except Exception as e:
        logger.error(f"LLM Layer One: Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page['id'],
            "error": str(e)
        }