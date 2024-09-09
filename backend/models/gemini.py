import json
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
Do you see the following keywords anywhere on the page? Format your response as a JSON object with the following structure:

{ 
  "reasoning": "I can clearly see that (at least one)/(none) of the given keywords is/are on the page.",
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

- Set "retrieval" to true if you find at least one keyword on the page, false otherwise.
- Only include the "keywords" array if "retrieval" is true.
- In the "keywords" array, only include keywords that were found on the page.
- For each keyword with found article(s), list all the articles on the page that the keyword belongs to.
- Provide the headline with a brief, informative 1-2 sentence summary for each article.

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

        # Extract keywords from the query
        keywords = query.split("Keywords:")[1].strip() if "Keywords:" in query else ""

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
            
            Keywords: {keywords}
            """
        ])
        
        # Attempt to parse the response as JSON
        try:
            json_response = json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON response for page {page['id']}. Using fallback response.")
            json_response = {
                "retrieval": False,
                "error": "Invalid JSON response from Gemini API"
            }
        
        logger.info(f"Successfully processed page {page['id']}")
        return {
            "page_id": f"{page['id'].split('_')[0]}_{page['number']}",
            "response": json.dumps(json_response)  # Ensure we're sending a valid JSON string
        }
    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": f"{page['id'].split('_')[0]}_{page['number']}",
            "response": json.dumps({
                "retrieval": False,
                "error": str(e)
            })
        }