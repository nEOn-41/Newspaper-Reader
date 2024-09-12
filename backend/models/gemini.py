import google.generativeai as genai
from config import GEMINI_API_KEY, UPLOAD_DIR
import io
from PIL import Image
import os
import logging
from models.system_prompt import get_system_prompt

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

async def process_page(page, pdf_data, query):
    try:
        logger.info(f"Processing page {page['id']}")
        
        # Open the image using PIL
        image_path = os.path.join(UPLOAD_DIR, page['id'].split('_')[0], f"{page['number']}.png")
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

        # Get the dynamic system prompt
        system_prompt = get_system_prompt()

        # Construct the full query
        full_query = f"""
        {system_prompt}
        Publication: {pdf_data['publication_name']}
        Edition: {pdf_data['edition']}
        Date: {pdf_data['date']}
        Page: {page['number']}
        
        {query}
        """

        response = await model.generate_content_async([
            {
                "mime_type": "image/png",
                "data": img_byte_arr
            },
            full_query
        ])
        
        logger.info(f"Successfully processed page {page['id']}")
        return {
            "page_id": f"{page['id'].split('_')[0]}_{page['number']}",
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": f"{page['id'].split('_')[0]}_{page['number']}",
            "error": str(e)
        }