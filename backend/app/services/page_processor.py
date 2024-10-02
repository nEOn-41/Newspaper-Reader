import os
import logging
from typing import Dict, Any
from ..config import UPLOAD_DIR

logger = logging.getLogger(__name__)

async def process_page(page: Dict[str, Any], pdf_data: Dict[str, Any], query: str, client_name: str) -> Dict[str, Any]:
    """
    Processes a single page through both LLM layers.

    This function coordinates the processing of a page through the first LLM layer for analysis
    and the second LLM layer for validation if necessary.

    Args:
        page (Dict[str, Any]): Dictionary containing page information.
        pdf_data (Dict[str, Any]): Metadata about the PDF containing the page.
        query (str): The query to be applied to the page.
        client_name (str): The name of the client for whom the processing is being performed.

    Returns:
        Dict[str, Any]: A dictionary containing the processing results or error information.

    Raises:
        Exception: If there's an error during the page processing.
    """
    try:
        logger.info(f"Processing page {page['id']}")
        image_path = os.path.join(UPLOAD_DIR, page['id'].split('_')[0], f"{page['number']}.png")
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {
                "page_id": page['id'],
                "error": f"Image file not found: {image_path}"
            }

        page['image_path'] = image_path

        from .llm_layer_one import analyze_page_with_llm_one
        from .llm_layer_two import validate_llm_one_response

        # Process with LLM Layer One
        llm_one_result = await analyze_page_with_llm_one(page, pdf_data, query, client_name)

        if llm_one_result.get("error"):
            logger.error(f"Error in LLM Layer One for page {page['id']}: {llm_one_result['error']}")
            return llm_one_result

        # Check if retrieval is true
        if llm_one_result["first_response"].get("retrieval"):
            # Process with LLM Layer Two
            try:
                llm_two_result = await validate_llm_one_response(
                    page_id=page['id'],
                    llm_one_response=llm_one_result["first_response"],
                    client_name=client_name
                )
                # Merge results
                return {**llm_one_result, **llm_two_result}
            except Exception as e:
                logger.error(f"Error in LLM Layer Two for page {page['id']}: {str(e)}")
                return {**llm_one_result, "error": f"Error in LLM Layer Two: {str(e)}"}
        else:
            # No need to process with the second LLM
            return llm_one_result

    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        logger.error(f"PDF data: {pdf_data}")
        return {
            "page_id": page['id'],
            "error": str(e)
        }