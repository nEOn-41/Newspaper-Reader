# retry_processor.py

import asyncio
import json
import logging
from models.gemini import process_page

logger = logging.getLogger(__name__)

def identify_failed_responses(responses):
    failed_responses = []
    valid_responses = []

    for response in responses:
        if isinstance(response, dict):
            if 'error' in response or 'first_response' not in response:
                failed_responses.append(response)
            else:
                valid_responses.append(response)
        else:
            logger.error(f"Invalid response type: {type(response)}")
            failed_responses.append({'error': 'Invalid response type', 'response': str(response)})

    return valid_responses, failed_responses

async def retry_failed_responses(failed_responses, query, client_name):
    logger.info(f"Retrying {len(failed_responses)} failed responses")
    retried_responses = []

    for response in failed_responses:
        if 'page_id' not in response or 'pdf_data' not in response:
            logger.error(f"Invalid response structure: {response}")
            continue

        page_id = response['page_id']
        pdf_data = response.get('pdf_data', {})
        page_number = int(page_id.split('_')[-1])
        page = {
            'id': page_id,
            'number': page_number,
            'pdf_data': pdf_data
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                retried_response = await process_page(page, pdf_data, query, client_name)
                retried_responses.append(retried_response)
                break  # Exit the retry loop on success
            except Exception as e:
                logger.error(f"Error retrying page {page['id']} (Attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)  # Wait before retrying

    return retried_responses
