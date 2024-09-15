# backend/app/services/pdf_processor.py

import os
import uuid
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
import logging
from ..utils.file_utils import save_image
from ..utils.general_utils import load_metadata, save_metadata
from ..config import UPLOAD_DIR, METADATA_FILE, PDF_EXTRACTION_ZOOM
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.metadata_file = METADATA_FILE
        os.makedirs(self.upload_dir, exist_ok=True)

    def generate_pdf_id(self):
        return str(uuid.uuid4())

    def extract_pages(self, pdf_content, pdf_id):
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            pdf_dir = Path(self.upload_dir) / pdf_id
            os.makedirs(pdf_dir, exist_ok=True)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(PDF_EXTRACTION_ZOOM, PDF_EXTRACTION_ZOOM)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                image_path = pdf_dir / f"{page_num + 1}.png"
                save_image(img, image_path)
            doc.close()
            logger.info(f"Extracted {len(doc)} pages from PDF {pdf_id}")
            return len(doc)
        except Exception as e:
            logger.error(f"Failed to extract pages for PDF {pdf_id}: {str(e)}")
            raise e

    def update_metadata(self, pdf_id, publication_name, edition, date, total_pages):
        try:
            metadata = load_metadata()
            metadata['pdfs'][pdf_id] = {
                "publication_name": publication_name,
                "edition": edition,
                "date": date,
                "total_pages": total_pages
            }
            save_metadata(metadata)
            logger.info(f"Updated metadata for PDF {pdf_id}")
        except Exception as e:
            logger.error(f"Failed to update metadata for PDF {pdf_id}: {str(e)}")
            raise e
