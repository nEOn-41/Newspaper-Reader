import asyncio
from models.gemini import process_page
import logging

logger = logging.getLogger(__name__)

async def process_batch(batch, query):
    logger.info(f"Processing batch of {len(batch)} pages")
    tasks = []
    for page in batch:
        task = asyncio.create_task(process_page(page, page["pdf_data"], query))
        tasks.append(task)
    
    try:
        batch_responses = await asyncio.gather(*tasks)
        logger.info(f"Successfully processed batch of {len(batch)} pages")
        return batch_responses
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        return []