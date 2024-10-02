import asyncio
import logging
from typing import List, Dict, Any, Tuple
from ..services.page_processor import process_page

logger = logging.getLogger(__name__)

def identify_failed_responses(responses: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Identifies and separates valid and failed responses.

    Args:
        responses (List[Dict[str, Any]]): A list of response dictionaries to be processed.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: A tuple containing two lists:
            1. Valid responses
            2. Failed responses
    """
    failed_responses = []
    valid_responses = []

    for response in responses:
        if isinstance(response, dict):
            if 'error' in response or 'first_response' not in response:
                failed_responses.append(response)
            else:
                valid_responses.append(response)
        else:
            logger.error(f"Invalid response type: {type(response)}")
            failed_responses.append({'error': 'Invalid response type', 'response': str(response)})

    return valid_responses, failed_responses

async def retry_failed_responses(failed_responses: List[Dict[str, Any]], query: str, client_name: str) -> List[Dict[str, Any]]:
    """
    Retries processing for failed responses.

    Args:
        failed_responses (List[Dict[str, Any]]): A list of failed response dictionaries to be retried.
        query (str): The query string used for processing.
        client_name (str): The name of the client for whom the processing is being done.

    Returns:
        List[Dict[str, Any]]: A list of retried response dictionaries.
    """
    logger.info(f"Retrying {len(failed_responses)} failed responses")
    retried_responses = []

    for response in failed_responses:
        if 'page_id' not in response:
            logger.error(f"Invalid response structure: {response}")
            continue

        page_id = response['page_id']
        pdf_data = response.get('pdf_data', {})
        page_number = int(page_id.split('_')[-1])
        page = {
            'id': page_id,
            'number': page_number,
            'pdf_data': pdf_data
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Retrying page {page['id']} (Attempt {attempt + 1}) with LLM Layer One")
                retried_response = await process_page(page, pdf_data, query, client_name)
                
                if 'error' not in retried_response:
                    logger.info(f"Successfully retried page {page['id']} with LLM Layer One")
                    retried_responses.append(retried_response)
                    break
                else:
                    logger.error(f"Error retrying page {page['id']} with LLM Layer One (Attempt {attempt + 1}): {retried_response['error']}")
            except Exception as e:
                logger.error(f"Exception retrying page {page['id']} with LLM Layer One (Attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(5)  # Wait before retrying
        else:
            logger.error(f"Failed to retry page {page['id']} after {max_retries} attempts")

    return retried_responses