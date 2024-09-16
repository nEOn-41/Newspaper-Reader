from fastapi import APIRouter
from ..utils.general_utils import load_metadata
from ..utils.custom_exceptions import PDFProcessingError
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/list-pdfs")
async def list_pdfs() -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves a list of all uploaded PDFs with their metadata.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of PDF metadata.

    Raises:
        PDFProcessingError: If there's an error retrieving the PDF list.
    """
    logger.info("Fetching list of PDFs")
    try:
        metadata = load_metadata()
        pdf_list: List[Dict[str, Any]] = []
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
    except Exception as e:
        logger.error(f"Error fetching PDF list: {str(e)}")
        raise PDFProcessingError(f"Error fetching PDF list: {str(e)}")