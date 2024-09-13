# models/gemini.py

import os
import io
import json
from PIL import Image
import logging
from models.system_prompt import get_system_prompt, get_second_system_prompt
from utils.request_pipeline import add_request_to_queue
from config import UPLOAD_DIR
from utils.utils import load_clients  # To get client details

logger = logging.getLogger(__name__)

async def process_page(page, pdf_data, query, client_name):
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

        response_text = response.text

        logger.info(f"Successfully processed page {page['id']} in first LLM")

        # Parse the first LLM response
        try:
            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from first LLM for page {page['id']}")
            return {
                "page_id": page['id'],
                "first_response": response_text,
                "error": "Invalid JSON response from first LLM"
            }

        # Check if retrieval is true
        if response_json.get("retrieval") == True:
            # Prepare content for the second LLM
            second_system_prompt = get_second_system_prompt()
            
            # Load client details
            clients = load_clients()
            client_data = clients.get(client_name, {})
            client_background = client_data.get("details", "No background provided.")
            
            # Format the second system prompt with client name and background
            second_system_prompt_formatted = second_system_prompt.format(
                client_name=client_name,
                client_background=client_background
            )

            # Prepare content for the second LLM
            second_content = [
                second_system_prompt_formatted,
                f"JSON Input:\n{json.dumps(response_json)}"
            ]

            # Add the request to the queue and await the result
            second_future = add_request_to_queue(second_content)
            second_response = await second_future

            second_response_text = second_response.text

            logger.info(f"Successfully processed page {page['id']} in second LLM")

            return {
                "page_id": page['id'],
                "first_response": response_text,
                "second_response": second_response_text
            }
        else:
            # No need to process with the second LLM
            return {
                "page_id": page['id'],
                "first_response": response_text
            }

    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page['id'],
            "error": str(e)
        }
