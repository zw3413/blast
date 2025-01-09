import asyncio
from typing import Optional

class FrameQueueSingleton:
    _instance: Optional['FrameQueueSingleton'] = None
    _queue: Optional[asyncio.Queue] = None

    def __new__(cls):
        if cls._instance is None:
            print(f"Creating new queue instance")
            cls._instance = super().__new__(cls)
            cls._queue = asyncio.Queue(maxsize=100)
        return cls._instance

    @classmethod
    def get_queue(cls) -> asyncio.Queue:
        if cls._instance is None:
            cls()
        print(f"Returning queue with ID: {id(cls._queue)}")
        return cls._queue