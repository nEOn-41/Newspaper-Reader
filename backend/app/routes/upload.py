from fastapi import APIRouter, File, UploadFile, Form
from ..services.pdf_processor import PDFProcessor
from ..utils.custom_exceptions import PDFUploadError, PDFProcessingError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
pdf_processor = PDFProcessor()

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    publication_name: str = Form(...),
    edition: str = Form(...),
    date: str = Form(...)
):
    """
    Handles the upload of a PDF file along with its metadata.

    This function processes the uploaded PDF, extracts its pages,
    and saves the associated metadata.

    Args:
        file (UploadFile): The PDF file to be uploaded.
        publication_name (str): The name of the publication.
        edition (str): The edition of the publication.
        date (str): The date of the publication.

    Returns:
        dict: A dictionary containing the PDF ID and a success message.

    Raises:
        PDFUploadError: If there's an error during the upload process.
        PDFProcessingError: If there's an error processing the PDF.
    """
    logger.info(f"Received file: {file.filename}")
    logger.info(f"Publication Name: {publication_name}")
    logger.info(f"Edition: {edition}")
    logger.info(f"Date: {date}")
    
    if file.content_type != "application/pdf":
        logger.warning(f"Rejected file: {file.filename} (not a PDF)")
        raise PDFUploadError("Only PDF files are allowed")
    
    try:
        # Read the uploaded file content
        pdf_content = await file.read()
        
        # Generate a unique identifier for this PDF
        pdf_id = pdf_processor.generate_pdf_id()
        
        # Extract pages and save images
        total_pages = pdf_processor.extract_pages(pdf_content, pdf_id)
        
        # Update metadata
        pdf_processor.update_metadata(pdf_id, publication_name, edition, date, total_pages)
        
        logger.info(f"Successfully processed PDF: {file.filename}")
        logger.info(f"Metadata file location: {pdf_processor.metadata_file}")
        
        return {"pdf_id": pdf_id, "message": "PDF uploaded and pages extracted successfully"}
    except Exception as e:
        logger.error(f"Error in upload_pdf: {str(e)}")
        raise PDFProcessingError(f"Error processing PDF: {str(e)}")