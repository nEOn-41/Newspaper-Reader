import os
import uuid
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
import logging
from typing import Dict, Any
from ..utils.file_utils import save_image
from ..utils.general_utils import load_metadata, save_metadata
from ..config import UPLOAD_DIR, METADATA_FILE, PDF_EXTRACTION_ZOOM

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    A class for processing PDF files, including extraction of pages and metadata management.
    """

    def __init__(self):
        """
        Initializes the PDFProcessor with the upload directory and metadata file path.
        """
        self.upload_dir: Path = UPLOAD_DIR
        self.metadata_file: Path = METADATA_FILE
        os.makedirs(self.upload_dir, exist_ok=True)

    def generate_pdf_id(self) -> str:
        """
        Generates a unique identifier for a PDF.

        Returns:
            str: A unique identifier (UUID) for the PDF.
        """
        return str(uuid.uuid4())

    def extract_pages(self, pdf_content: bytes, pdf_id: str) -> int:
        """
        Extracts pages from a PDF and saves them as images.

        Args:
            pdf_content (bytes): The content of the PDF file.
            pdf_id (str): The unique identifier for the PDF.

        Returns:
            int: The total number of pages extracted.

        Raises:
            Exception: If there's an error during page extraction.
        """
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

    def update_metadata(self, pdf_id: str, publication_name: str, edition: str, date: str, total_pages: int) -> None:
        """
        Updates the metadata for a processed PDF.

        Args:
            pdf_id (str): The unique identifier for the PDF.
            publication_name (str): The name of the publication.
            edition (str): The edition of the publication.
            date (str): The date of the publication.
            total_pages (int): The total number of pages in the PDF.

        Raises:
            Exception: If there's an error updating the metadata.
        """
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