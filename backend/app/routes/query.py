from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from ..models.system_prompt import get_system_prompt, get_additional_query
from ..utils.general_utils import load_metadata, get_pdf_count
from ..utils.batch_processing import process_batch
from ..utils.retry_processor import identify_failed_responses, retry_failed_responses
from ..utils.custom_exceptions import QueryProcessingError, RateLimitExceededError
import logging
from ..services.page_processor import process_page

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    """
    Pydantic model for query request data.
    """
    client: str
    keywords: List[str]
    additional_query: str = ""

@router.post("/query")
async def query_pdf(request: QueryRequest) -> Dict[str, List[Dict[str, Any]]]:
    """
    Processes a query request for PDF analysis.

    This function handles the entire process of querying PDFs based on client keywords,
    processing pages, and returning the results.

    Args:
        request (QueryRequest): The query request containing client, keywords, and additional query.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of responses for each processed page.

    Raises:
        QueryProcessingError: If an error occurs during query processing.
    """
    client = request.client
    keywords = request.keywords
    additional_query = request.additional_query
    responses: List[Dict[str, Any]] = []
    
    logger.info(f"Received query for client: {client}")
    
    try:
        metadata = load_metadata()
        extracted_pages = metadata.get("pdfs", {})
        pdf_count = get_pdf_count()
        logger.info(f"Total PDFs in metadata: {pdf_count}")
        
        system_prompt = get_system_prompt()
        default_additional_query = get_additional_query()
        
        full_query = f"{default_additional_query} {additional_query}\nKeywords: {', '.join(keywords)}"
        
        logger.info(f"Number of PDFs to process: {len(extracted_pages)}")
        
        if len(extracted_pages) == 0:
            logger.warning("No PDFs found in metadata. Check if PDFs are being properly saved.")
            return {"responses": [], "message": "No PDFs found to process"}
        
        tasks = []
        for pdf_id, pdf_data in extracted_pages.items():
            total_pages = pdf_data.get("total_pages", 0)
            logger.info(f"Processing PDF {pdf_id} with {total_pages} pages")
            
            for page_num in range(total_pages):
                page = {
                    "id": f"{pdf_id}_{page_num+1}",
                    "number": page_num+1,
                    "pdf_data": pdf_data
                }
                tasks.append(process_page(page, pdf_data, full_query, client))
        
        responses = await asyncio.gather(*tasks)
        
        valid_responses, failed_responses = identify_failed_responses(responses)
        
        if failed_responses:
            retried_responses = await retry_failed_responses(failed_responses, full_query, client)
            valid_responses.extend(retried_responses)
        
        logger.info(f"Query processing complete. Total responses: {len(valid_responses)}")
        return {"responses": [
            {
                "page_id": r.get("page_id"),
                "first_response": r.get("first_response"),
                "second_response": r.get("second_response")
            } 
            for r in valid_responses if r.get("page_id")
        ]}

    except Exception as e:
        logger.error(f"An error occurred during query processing: {str(e)}")
        raise QueryProcessingError(f"An error occurred during query processing: {str(e)}")