import asyncio
import logging
from typing import List, Dict, Any
from collections import deque
from time import time
from ..config import RATE_LIMIT_INTERVAL, BATCH_SIZE
from ..models.gemini_model import model
from aiolimiter import AsyncLimiter

logger = logging.getLogger(__name__)

# Global request queue
request_queue: asyncio.Queue = asyncio.Queue()

# Rate limiter
rate_limiter = AsyncLimiter(BATCH_SIZE, RATE_LIMIT_INTERVAL)

# Sliding window buffer
request_buffer: deque = deque()

async def request_worker() -> None:
    while True:
        current_time = time()
        
        # Remove expired requests from the buffer
        while request_buffer and current_time - request_buffer[0] >= RATE_LIMIT_INTERVAL:
            request_buffer.popleft()
        
        # Process as many requests as possible
        available_slots = BATCH_SIZE - len(request_buffer)
        if available_slots > 0:
            batch = []
            for _ in range(available_slots):
                try:
                    task = request_queue.get_nowait()
                    batch.append(task)
                except asyncio.QueueEmpty:
                    break
            
            if batch:
                await process_batch(batch)
                current_time = time()
                request_buffer.extend([current_time] * len(batch))
        
        # Wait a short time before checking again
        await asyncio.sleep(0.1)

async def process_batch(batch: List[Dict[str, Any]]) -> None:
    async with rate_limiter:
        tasks = [process_request(task) for task in batch]
        await asyncio.gather(*tasks)

async def process_request(task: Dict[str, Any]) -> None:
    content = task['content']
    future = task['future']
    try:
        response = await model.generate_content_async(content)
        future.set_result(response)
    except Exception as e:
        future.set_exception(e)

def add_request_to_queue(content: List[Any]) -> asyncio.Future:
    future = asyncio.get_event_loop().create_future()
    request_queue.put_nowait({'content': content, 'future': future})
    return future