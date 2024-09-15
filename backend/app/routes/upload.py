# backend/app/routes/upload.py

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from services.pdf_processor import PDFProcessor
from utils.api_utils import success_response, error_response
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
    logger.info(f"Received file: {file.filename}")
    logger.info(f"Publication Name: {publication_name}")
    logger.info(f"Edition: {edition}")
    logger.info(f"Date: {date}")
    
    if file.content_type != "application/pdf":
        logger.warning(f"Rejected file: {file.filename} (not a PDF)")
        return error_response("Only PDF files are allowed", status_code=400)
    
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
        
        return success_response({"pdf_id": pdf_id}, "PDF uploaded and pages extracted successfully")
    except Exception as e:
        logger.error(f"Error in upload_pdf: {str(e)}")
        return error_response(f"Error uploading PDF: {str(e)}", status_code=500)
