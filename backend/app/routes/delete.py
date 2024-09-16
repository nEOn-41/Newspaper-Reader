from fastapi import APIRouter, HTTPException
import shutil
from typing import Dict
from ..utils.general_utils import load_metadata, save_metadata
from ..config import UPLOAD_DIR

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
        HTTPException: If the PDF is not found.
    """
    metadata = load_metadata()
    
    if pdf_id not in metadata['pdfs']:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Remove the PDF directory
    pdf_dir = UPLOAD_DIR / pdf_id
    if pdf_dir.exists():
        shutil.rmtree(pdf_dir)
    
    # Remove the PDF from metadata
    del metadata['pdfs'][pdf_id]
    
    # Save updated metadata
    save_metadata(metadata)
    
    return {"message": f"PDF with id {pdf_id} has been deleted"}