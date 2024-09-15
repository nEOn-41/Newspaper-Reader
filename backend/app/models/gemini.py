# backend/app/models/gemini.py

import os
import io
import json
from PIL import Image
import logging
from ..services.llm_layer_one import analyze_page_with_llm_one
from ..services.llm_layer_two import validate_llm_one_response
from ..utils.general_utils import load_clients
from ..config import UPLOAD_DIR

logger = logging.getLogger(__name__)

async def process_page(page, pdf_data, query, client_name):
    try:
        logger.info(f"Processing page {page['id']}")
        # Assuming 'image_path' is part of the page data
        image_path = os.path.join(UPLOAD_DIR, page['id'].split('_')[0], f"{page['number']}.png")

        # Process with LLM Layer One
        llm_one_result = await analyze_page_with_llm_one(page, pdf_data, query, client_name)

        if llm_one_result.get("error"):
            return llm_one_result

        # Check if retrieval is true
        if llm_one_result["first_response"].get("retrieval"):
            # Process with LLM Layer Two
            llm_two_result = await validate_llm_one_response(
                page_id=page['id'],
                llm_one_response=llm_one_result["first_response"],
                client_name=client_name
            )
            # Merge results
            return {**llm_one_result, **llm_two_result}
        else:
            # No need to process with the second LLM
            return llm_one_result

    except Exception as e:
        logger.error(f"Error processing page {page['id']}: {str(e)}")
        return {
            "page_id": page['id'],
            "error": str(e)
        }
