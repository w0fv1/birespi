import enum
from typing import TypeVar, Generic

from model.LiveEventMessage import DanmuMessageData, LiveMessage


class TaskType(enum.Enum):
    ReplyDanmu = "ReplyDanmu"


T = TypeVar("T")


class TaskData(Generic[T]):
    def getData(self) -> T:
        pass


class DanmuTaskData(TaskData[LiveMessage[DanmuMessageData]]):
    danmu: LiveMessage[DanmuMessageData]

    def __init__(self, danmu: LiveMessage[DanmuMessageData]):
        self.danmu = danmu

    def getData(self) -> LiveMessage[DanmuMessageData]:
        return self.danmu


# 基于TaskData的泛型


class Task(Generic[T]):

    taskType: TaskType
    taskData: TaskData[T]
    priority: int = (
        0  # 0 is the lowest priority, the higher the number, the higher the priority
    )
    # 1为普通任务，10为最紧急任务,5为一般紧急任务

    def __init__(self, task_type: TaskType, task_data: TaskData[T], priority: int = 0):
        self.taskType = task_type
        self.taskData = task_data
        self.priority = priority

    @staticmethod
    def ReplyDanmu(
        danmu: LiveMessage[DanmuMessageData],
    ) -> "Task[LiveMessage[DanmuMessageData]]":
        return Task(TaskType.ReplyDanmu, DanmuTaskData(danmu), 1)
