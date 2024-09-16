from fastapi import APIRouter
import shutil
from typing import Dict
from ..utils.general_utils import load_metadata, save_metadata
from ..config import UPLOAD_DIR
from ..utils.custom_exceptions import ResourceNotFoundError, PDFProcessingError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.delete("/delete-pdf/{pdf_id}")
async def delete_pdf(pdf_id: str) -> Dict[str, str]:
    """
    Deletes a PDF and its associated metadata.

    Args:
        pdf_id (str): The unique identifier of the PDF to be deleted.

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        ResourceNotFoundError: If the PDF is not found.
        PDFProcessingError: If there's an error deleting the PDF.
    """
    metadata = load_metadata()
    
    if pdf_id not in metadata['pdfs']:
        raise ResourceNotFoundError("PDF", pdf_id)
    
    try:
        # Remove the PDF directory
        pdf_dir = UPLOAD_DIR / pdf_id
        if pdf_dir.exists():
            shutil.rmtree(pdf_dir)
        
        # Remove the PDF from metadata
        del metadata['pdfs'][pdf_id]
        
        # Save updated metadata
        save_metadata(metadata)
        
        logger.info(f"PDF with id {pdf_id} has been deleted")
        return {"message": f"PDF with id {pdf_id} has been deleted"}
    except Exception as e:
        logger.error(f"Error deleting PDF {pdf_id}: {str(e)}")
        raise PDFProcessingError(f"Error deleting PDF {pdf_id}: {str(e)}")