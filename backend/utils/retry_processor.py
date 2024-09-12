import asyncio
import json
import logging
from models.gemini import process_page

logger = logging.getLogger(__name__)

async def retry_failed_responses(failed_responses, query):
    logger.info(f"Retrying {len(failed_responses)} failed responses")
    retried_responses = []

    for response in failed_responses:
        # Check if 'page' and 'pdf_data' keys exist in the response
        if 'page' not in response or 'pdf_data' not in response:
            logger.error(f"Invalid response structure: {response}")
            continue

        page = response['page']
        pdf_data = response['pdf_data']
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                retried_response = await process_page(page, pdf_data, query)
                
                # Validate the response structure
                if 'page_id' in retried_response and 'response' in retried_response:
                    try:
                        json.loads(retried_response['response'])  # Check if it's valid JSON
                        retried_responses.append(retried_response)
                        break  # Success, exit retry loop
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in response for page {page['id']} (Attempt {attempt + 1})")
                else:
                    logger.warning(f"Invalid response structure for page {page['id']} (Attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error processing page {page['id']} (Attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(5)  # Wait 5 seconds before retrying
    
    return retried_responses

def identify_failed_responses(responses):
    failed_responses = []
    valid_responses = []

    for response in responses:
        if isinstance(response, dict):
            if 'error' in response or 'response' not in response:
                failed_responses.append(response)
            else:
                try:
                    json.loads(response['response'])  # Check if it's valid JSON
                    valid_responses.append(response)
                except json.JSONDecodeError:
                    failed_responses.append(response)
        else:
            logger.error(f"Invalid response type: {type(response)}")
            failed_responses.append({'error': 'Invalid response type', 'response': str(response)})

    return valid_responses, failed_responses