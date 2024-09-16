import asyncio
from typing import List, Dict, Any
from ..services.page_processor import process_page
import logging

logger = logging.getLogger(__name__)

async def process_batch(batch: List[Dict[str, Any]], query: str, client_name: str) -> List[Dict[str, Any]]:
    """
    Processes a batch of pages asynchronously.

    This function takes a batch of pages and processes each page using the process_page function.
    It handles the concurrent execution of page processing tasks.

    Args:
        batch (List[Dict[str, Any]]): A list of dictionaries, each containing data for a single page.
        query (str): The query string to be applied to each page.
        client_name (str): The name of the client for whom the processing is being done.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the processing results for each page.

    Raises:
        Exception: If there's an error during batch processing.
    """
    logger.info(f"Processing batch of {len(batch)} pages")
    tasks = []
    for page in batch:
        task = asyncio.create_task(process_page(page, page["pdf_data"], query, client_name))
        tasks.append(task)
    
    try:
        batch_responses = await asyncio.gather(*tasks)
        logger.info(f"Successfully processed batch of {len(batch)} pages")
        return batch_responses
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        return []