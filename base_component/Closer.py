import asyncio
import threading
from typing import List


class Closer:
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.threads: List[threading.Thread] = []

    def add_task(self, task: asyncio.Task):
        self.tasks.append(task)

    def add_thread(self, thread: threading.Thread):
        self.threads.append(thread)

    async def close(self):
        for task in self.tasks:
            task.cancel()

        for thread in self.threads:
            thread.join()


class CloserHolder:
    closer: Closer = None

    def set(self, closer: Closer):
        self.closer = closer

    def get(self) -> Closer:
        return self.closer


closerHolder: CloserHolder = CloserHolder()


def getCloser() -> Closer:
    return closerHolder.get()
