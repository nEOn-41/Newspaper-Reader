from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import fitz
from PIL import Image
import io
from pathlib import Path
from utils.utils import save_metadata, load_metadata
from config import UPLOAD_DIR, METADATA_FILE, PDF_EXTRACTION_ZOOM
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

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
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read the uploaded file content
        pdf_content = await file.read()
        
        # Generate a unique identifier for this PDF
        pdf_id = str(uuid.uuid4())
        
        # Create a directory for this PDF
        pdf_dir = UPLOAD_DIR / pdf_id
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Open the PDF using PyMuPDF
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        # Load existing metadata
        metadata = load_metadata()
        
        # Store extracted pages and metadata
        metadata['pdfs'][pdf_id] = {
            "publication_name": publication_name,
            "edition": edition,
            "date": date,
            "total_pages": len(doc)
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Set zoom to 2.0 for better quality, especially for vector content
            zoom = PDF_EXTRACTION_ZOOM
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert PyMuPDF pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            image_path = os.path.join(pdf_dir, f"{page_num + 1}.png")
            
            # Save the image as PNG with high quality
            img.save(image_path, "PNG", quality=95)
        
        doc.close()
        
        # Save updated metadata
        save_metadata(metadata)
        
        logger.info(f"Successfully processed PDF: {file.filename}")
        logger.info(f"Metadata file location: {METADATA_FILE}")
        logger.info(f"Current metadata content: {metadata}")
        
        return JSONResponse(content={"message": "PDF uploaded and pages extracted successfully", "pdf_id": pdf_id})
    except Exception as e:
        logger.error(f"Error in upload_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading PDF: {str(e)}")

@router.get("/list-pdfs")
async def list_pdfs():
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