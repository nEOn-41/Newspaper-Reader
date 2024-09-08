from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from PIL import Image
import io
from models.gemini import process_page
from utils.utils import load_metadata
from utils.batch_processing import process_batch
from config import UPLOAD_DIR
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def query_pdf(request: QueryRequest):
    query = request.query
    responses = []
    
    logger.info(f"Received query: {query}")
    
    extracted_pages = load_metadata()
    logger.info(f"Number of PDFs to process: {len(extracted_pages)}")
    
    batch_size = 15
    current_batch = []
    
    for pdf_id, pdf_data in extracted_pages.items():
        total_pages = pdf_data["total_pages"]
        logger.info(f"Processing PDF {pdf_id} with {total_pages} pages")
        
        for page_num in range(total_pages):
            current_batch.append({
                "id": f"{pdf_id}_{page_num+1}",
                "number": page_num+1,
                "pdf_data": pdf_data
            })
            
            if len(current_batch) == batch_size:
                responses.extend(await process_batch(current_batch, query))
                current_batch = []
                
                logger.info("Rate limit reached. Waiting for 60 seconds...")
                await asyncio.sleep(60)
    
    # Process any remaining pages in the last batch
    if current_batch:
        responses.extend(await process_batch(current_batch, query))
    
    logger.info(f"Query processing complete. Total responses: {len(responses)}")
    return {"responses": responses}