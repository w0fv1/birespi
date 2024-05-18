from typing import TypeVar, Generic, Optional
from collections import deque
from threading import Lock

T = TypeVar('T')  # 定义一个类型变量T

class FastConsumptionQueue(Generic[T]):

    queue: deque
    lock: Lock

    def __init__(self):
        self.queue = deque()  # 使用双端队列存储数据
        self.lock = Lock()    # 线程锁，保证数据安全

    def push(self, data: T) -> None:
        """
        添加数据到队列。每秒钟可以添加多个数据。
        """
        with self.lock:
            self.queue.append(data)

    def pop(self) -> Optional[T]:
        """
        消费一条数据，并丢弃其他数据。这个操作大约发生在5到10秒一次。
        通过调用select_data方法来决定返回哪条数据。
        """
        with self.lock:
            if self.queue:
                item = self.select_data(self.queue)
                self.queue.clear()  # 清空队列
                return item
            return None  # 如果队列为空，返回None

    def select_data(self, queue: deque) -> T:
        """
        从队列中选择一条数据返回。可以根据需要重写这个方法。
        默认实现返回最后一条数据。
        """
        return queue[-1]

    def size(self) -> int:
        """
        返回队列中的数据数量。
        """
        with self.lock:
            return len(self.queue)

    def clear(self) -> None:
        """
        清空队列中的所有数据。
        """
        with self.lock:
            self.queue.clear()
