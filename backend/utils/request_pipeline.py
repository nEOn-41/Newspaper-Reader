# utils/request_pipeline.py

import asyncio
import logging
from config import BATCH_SIZE, RATE_LIMIT_INTERVAL
from models.gemini_model import model  # Import model from gemini_model.py

logger = logging.getLogger(__name__)

# Global request queue
request_queue = asyncio.Queue()

async def request_worker():
    while True:
        batch = []
        for _ in range(BATCH_SIZE):
            try:
                task = await asyncio.wait_for(request_queue.get(), timeout=1)
                batch.append(task)
            except asyncio.TimeoutError:
                break
        if batch:
            await process_batch(batch)
            logger.info(f"Processed batch of {len(batch)} requests. Waiting for {RATE_LIMIT_INTERVAL} seconds.")
            await asyncio.sleep(RATE_LIMIT_INTERVAL)
        else:
            await asyncio.sleep(1)  # Avoid busy waiting

async def process_batch(batch):
    tasks = []
    for task in batch:
        content = task['content']
        future = task['future']
        tasks.append(asyncio.create_task(send_request_to_gemini_api(content, future)))
    await asyncio.gather(*tasks)

async def send_request_to_gemini_api(content, future):
    try:
        response = await model.generate_content_async(content)
        future.set_result(response)
    except Exception as e:
        future.set_exception(e)

def add_request_to_queue(content):
    future = asyncio.get_event_loop().create_future()
    request_queue.put_nowait({'content': content, 'future': future})
    return future
