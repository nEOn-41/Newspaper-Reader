from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from models.gemini import process_page
from utils.utils import load_metadata
from utils.batch_processing import process_batch
from config import UPLOAD_DIR
from routes.clients import load_clients
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    client: str

@router.post("/query")
async def query_pdf(request: QueryRequest):
    client = request.client
    responses = []
    
    logger.info(f"Received query for client: {client}")
    
    metadata = load_metadata()
    extracted_pages = metadata.get("pdfs", {})
    clients = load_clients()
    
    if client not in clients:
        raise HTTPException(status_code=404, detail="Client not found")
    
    keywords = clients[client]
    full_query = f"Can you find any article on the page with the following keywords: {', '.join(keywords)}?"
    
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
                responses.extend(await process_batch(current_batch, full_query))
                current_batch = []
                
                logger.info("Rate limit reached. Waiting for 60 seconds...")
                await asyncio.sleep(60)
    
    # Process any remaining pages in the last batch
    if current_batch:
        responses.extend(await process_batch(current_batch, full_query))
    
    logger.info(f"Query processing complete. Total responses: {len(responses)}")
    return {"responses": [{"page_id": r["page_id"], "response": r["response"]} for r in responses]}