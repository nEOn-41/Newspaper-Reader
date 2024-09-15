# query.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio
from models.gemini import process_page
from models.system_prompt import get_system_prompt, get_additional_query
from utils.general_utils import load_metadata, get_pdf_count
from utils.batch_processing import process_batch
from utils.retry_processor import identify_failed_responses, retry_failed_responses
from config import UPLOAD_DIR, METADATA_FILE
import logging
import os
import json

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    client: str
    keywords: List[str]
    additional_query: str = ""

@router.post("/query")
async def query_pdf(request: QueryRequest):
    client = request.client
    keywords = request.keywords
    additional_query = request.additional_query
    responses = []
    
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
        
        batch_size = 15
        current_batch = []
        
        for pdf_id, pdf_data in extracted_pages.items():
            total_pages = pdf_data.get("total_pages", 0)
            logger.info(f"Processing PDF {pdf_id} with {total_pages} pages")
            
            for page_num in range(total_pages):
                current_batch.append({
                    "id": f"{pdf_id}_{page_num+1}",
                    "number": page_num+1,
                    "pdf_data": pdf_data
                })
                
                if len(current_batch) == batch_size:
                    batch_responses = await process_batch(current_batch, full_query, client)
                    valid_responses, failed_responses = identify_failed_responses(batch_responses)
                    responses.extend(valid_responses)
                    
                    if failed_responses:
                        retried_responses = await retry_failed_responses(failed_responses, full_query, client)
                        responses.extend(retried_responses)
                    
                    current_batch = []
                    
                    logger.info("Rate limit reached. Waiting for 60 seconds...")
                    await asyncio.sleep(60)
        
        # Process any remaining pages in the last batch
        if current_batch:
            batch_responses = await process_batch(current_batch, full_query, client)
            valid_responses, failed_responses = identify_failed_responses(batch_responses)
            responses.extend(valid_responses)
            
            if failed_responses:
                retried_responses = await retry_failed_responses(failed_responses, full_query, client)
                responses.extend(retried_responses)
        
        logger.info(f"Query processing complete. Total responses: {len(responses)}")
        return {"responses": [
            {
                "page_id": r.get("page_id"),
                "first_response": r.get("first_response"),
                "second_response": r.get("second_response")
            } 
            for r in responses if r.get("page_id")
        ]}

    except Exception as e:
        logger.error(f"An error occurred during query processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during query processing: {str(e)}")
