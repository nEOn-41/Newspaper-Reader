import google.generativeai as genai
from config import GEMINI_API_KEY, UPLOAD_DIR
import io
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create the model
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

SYSTEM_PROMPT = """
You are an AI assistant specialized in analyzing newspaper pages. Your task is to examine the given newspaper page image and respond to queries about its content. Follow these guidelines:

1. Analyze the provided newspaper page image carefully.
2. Focus on finding information related to the given KEYWORDS in the query.
3. Provide concise and relevant responses.
4. Format your response as a JSON object with the following structure:

{
  "retrieval": boolean,
  "keywords": [
    {
      "keyword": string,
      "articles": [
        {
          "headline": string,
          "summary": string
        }
      ]
    }
  ]
}

- Set "retrieval" to true if any relevant information is found for at least one keyword, false otherwise.
- Only include the "keywords" array if "retrieval" is true.
- In the "keywords" array, only include keywords for which articles were found.
- For each keyword with found articles, list all related articles on the page.
- Provide a brief, informative summary for each article.

Remember to consider the provided metadata (Publication, Edition, Date, Page) when analyzing the content.
"""

async def process_page(page, pdf_data, query):
    try:
        logger.info(f"Processing page {page['id']}")
        
        # Open the image using PIL
        image_path = os.path.join(UPLOAD_DIR, page['id'].split('_')[0], f"{page['number']}.png")
        with Image.open(image_path) as img:
            # Convert the image to RGB mode if it's not already
            img = img.convert('RGB')
            
            # Create a byte stream of the image
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

        response = await model.generate_content_async([
            {
                "mime_type": "image/png",
                "data": img_byte_arr
            },
            f"""
            {SYSTEM_PROMPT}
            Publication: {pdf_data['publication_name']}
            Edition: {pdf_data['edition']}
            Date: {pdf_data['date']}
            Page: {page['number']}
            
            Query: {query}
            """
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