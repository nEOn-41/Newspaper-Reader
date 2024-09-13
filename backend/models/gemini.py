# models/gemini.py

import os
import io
from PIL import Image
import logging
from models.system_prompt import get_system_prompt
from utils.request_pipeline import add_request_to_queue
from config import UPLOAD_DIR

logger = logging.getLogger(__name__)

async def process_page(page, pdf_data, query):
    try:
        logger.info(f"Processing page {page['id']}")
        image_path = os.path.join(UPLOAD_DIR, page['id'].split('_')[0], f"{page['number']}.png")
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

        system_prompt = get_system_prompt()
        content = [
            {
                "mime_type": "image/png",
                "data": img_byte_arr
            },
            f"""
            {system_prompt}
            Publication: {pdf_data['publication_name']}
            Edition: {pdf_data['edition']}
            Date: {pdf_data['date']}
            Page: {page['number']}
            
            Query: {query}
            """
        ]

        # Add the request to the queue and await the result
        future = add_request_to_queue(content)
        response = await future

        logger.info(f"Successfully processed page {page['id']}")
        return {
            "page_id": page['id'],
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page['id'],
            "error": str(e)
        }
