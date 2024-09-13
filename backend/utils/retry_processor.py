import asyncio
import json
import logging
from models.gemini import process_page
from utils.request_pipeline import add_request_to_queue

logger = logging.getLogger(__name__)

def remove_duplicate_articles(keyword_data):
    if 'articles' not in keyword_data:
        return keyword_data
    seen = set()
    unique_articles = []
    for article in keyword_data['articles']:
        article_tuple = (article.get('headline', ''), article.get('summary', ''))
        if article_tuple not in seen:
            seen.add(article_tuple)
            unique_articles.append(article)
    keyword_data['articles'] = unique_articles
    return keyword_data

def clean_response(response_data):
    if isinstance(response_data, str):
        try:
            response_data = json.loads(response_data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in response: {response_data}")
            return None

    if not isinstance(response_data, dict):
        logger.error(f"Invalid response structure: {response_data}")
        return None

    # Handle the case where retrieval is false
    if 'retrieval' in response_data and response_data['retrieval'] is False:
        return response_data

    # If keywords exist, remove duplicate articles
    if 'keywords' in response_data:
        response_data['keywords'] = [remove_duplicate_articles(keyword) for keyword in response_data['keywords']]

    return response_data

async def retry_failed_responses(failed_responses, query):
    logger.info(f"Retrying {len(failed_responses)} failed responses")
    retried_responses = []

    for response in failed_responses:
        if 'page' not in response or 'pdf_data' not in response:
            logger.error(f"Invalid response structure: {response}")
            continue

        page = response['page']
        pdf_data = response['pdf_data']

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Prepare content as in process_page
                content = ...  # Same as in process_page
                future = add_request_to_queue(content)
                retried_response = await future

                # Process the retried_response as needed
                ...

                retried_responses.append(retried_response)
                break  # Exit the retry loop on success
            except Exception as e:
                logger.error(f"Error retrying page {page['id']} (Attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)  # Wait before retrying

    return retried_responses

def identify_failed_responses(responses):
    failed_responses = []
    valid_responses = []

    for response in responses:
        if isinstance(response, dict):
            if 'error' in response or 'response' not in response:
                failed_responses.append(response)
            else:
                cleaned_response = clean_response(response['response'])
                if cleaned_response is not None:
                    response['response'] = json.dumps(cleaned_response)
                    valid_responses.append(response)
                else:
                    failed_responses.append(response)
        else:
            logger.error(f"Invalid response type: {type(response)}")
            failed_responses.append({'error': 'Invalid response type', 'response': str(response)})

    return valid_responses, failed_responses