# backend/app/routes/pdfs.py

from fastapi import APIRouter, HTTPException
from utils.general_utils import load_metadata
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/list-pdfs")
async def list_pdfs():
    """
    Retrieves a list of all uploaded PDFs with their metadata.
    """
    logger.info("Fetching list of PDFs")
    metadata = load_metadata()
    pdf_list = []
    for pdf_id, pdf_data in metadata.get('pdfs', {}).items():
        pdf_list.append({
            "pdf_id": pdf_id,
            "publication_name": pdf_data.get("publication_name", "Unknown"),
            "edition": pdf_data.get("edition", "Unknown"),
            "date": pdf_data.get("date", "Unknown"),
            "page_count": pdf_data.get("total_pages", 0)
        })
    logger.info(f"Returning list of {len(pdf_list)} PDFs")
    return {"pdfs": pdf_list}
