import asyncio
import logging
from typing import List, Dict, Any
from ..config import BATCH_SIZE, RATE_LIMIT_INTERVAL
from ..models.gemini_model import model

logger = logging.getLogger(__name__)

# Global request queue
request_queue: asyncio.Queue = asyncio.Queue()

async def request_worker() -> None:
    """
    A worker function that continuously processes requests from the queue.

    This function runs indefinitely, processing batches of requests and enforcing rate limits.
    """
    while True:
        batch: List[Dict[str, Any]] = []
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

async def process_batch(batch: List[Dict[str, Any]]) -> None:
    """
    Processes a batch of requests concurrently.

    Args:
        batch (List[Dict[str, Any]]): A list of request tasks to be processed.
    """
    tasks = []
    for task in batch:
        content = task['content']
        future = task['future']
        tasks.append(asyncio.create_task(send_request_to_gemini_api(content, future)))
    await asyncio.gather(*tasks)

async def send_request_to_gemini_api(content: List[Any], future: asyncio.Future) -> None:
    """
    Sends a request to the Gemini API and sets the result in the provided future.

    Args:
        content (List[Any]): The content to be sent to the Gemini API.
        future (asyncio.Future): A future object to store the API response.
    """
    try:
        response = await model.generate_content_async(content)
        future.set_result(response)
    except Exception as e:
        future.set_exception(e)

def add_request_to_queue(content: List[Any]) -> asyncio.Future:
    """
    Adds a request to the global request queue.

    Args:
        content (List[Any]): The content of the request to be added to the queue.

    Returns:
        asyncio.Future: A future object that will eventually contain the result of the request.
    """
    future = asyncio.get_event_loop().create_future()
    request_queue.put_nowait({'content': content, 'future': future})
    return future