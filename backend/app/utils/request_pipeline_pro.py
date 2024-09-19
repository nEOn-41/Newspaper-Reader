# backend/app/utils/request_pipeline_pro.py

import asyncio
import logging
from typing import List, Dict, Any
from collections import deque
from time import time
from ..config import RATE_LIMIT_INTERVAL_PRO, BATCH_SIZE_PRO
from ..models.gemini_model_pro import model_pro
from aiolimiter import AsyncLimiter

logger = logging.getLogger(__name__)

# Global request queue for the pro model
request_queue_pro: asyncio.Queue = asyncio.Queue()

# Rate limiter for the pro model
rate_limiter_pro = AsyncLimiter(BATCH_SIZE_PRO, RATE_LIMIT_INTERVAL_PRO)

# Sliding window buffer for the pro model
request_buffer_pro: deque = deque()

async def request_worker_pro() -> None:
    while True:
        current_time = time()

        # Remove expired requests from the buffer
        while request_buffer_pro and current_time - request_buffer_pro[0] >= RATE_LIMIT_INTERVAL_PRO:
            request_buffer_pro.popleft()

        # Process as many requests as possible
        available_slots = BATCH_SIZE_PRO - len(request_buffer_pro)
        if available_slots > 0:
            batch = []
            for _ in range(available_slots):
                try:
                    task = request_queue_pro.get_nowait()
                    batch.append(task)
                except asyncio.QueueEmpty:
                    break

            if batch:
                await process_batch_pro(batch)
                current_time = time()
                request_buffer_pro.extend([current_time] * len(batch))

        # Wait a short time before checking again
        await asyncio.sleep(0.1)

async def process_batch_pro(batch: List[Dict[str, Any]]) -> None:
    async with rate_limiter_pro:
        tasks = [process_request_pro(task) for task in batch]
        await asyncio.gather(*tasks)

async def process_request_pro(task: Dict[str, Any]) -> None:
    content = task['content']
    future = task['future']
    try:
        response = await model_pro.generate_content_async(content)
        future.set_result(response)
    except Exception as e:
        future.set_exception(e)

def add_request_to_queue_pro(content: List[Any]) -> asyncio.Future:
    future = asyncio.get_event_loop().create_future()
    request_queue_pro.put_nowait({'content': content, 'future': future})
    return future
