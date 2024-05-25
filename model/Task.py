from enum import Enum
import json
from typing import TypeVar, Generic
import uuid

from pydantic import BaseModel
from model.LiveEventMessage import DanmuMessageData, LiveMessage


class TaskType(Enum):
    ReplyDanmu = "ReplyDanmu"


T = TypeVar("T")


class TaskData(BaseModel, Generic[T]):
    def getData(self) -> T:
        pass


class DanmuTaskData(TaskData[LiveMessage]):
    danmu: LiveMessage

    def __init__(self, danmu: LiveMessage[DanmuMessageData]):
        super().__init__(danmu=danmu)
        self.danmu = danmu

    def getData(self) -> LiveMessage[DanmuMessageData]:
        return self.danmu


# 基于TaskData的泛型


class Task(BaseModel, Generic[T]):
    id: str = ""
    taskType: TaskType
    taskData: TaskData[T]
    priority: int = (
        0  # 0 is the lowest priority, the higher the number, the higher the priority
    )
    # 1为普通任务，10为最紧急任务,5为一般紧急任务

    def __init__(self, taskType: TaskType, taskData: TaskData[T], priority: int = 0):
        id = str(uuid.uuid4())
        super().__init__(taskType=taskType, taskData=taskData, priority=priority, id=id)
        self.id = id
        self.taskType = taskType
        self.taskData = taskData
        print(f"Task: {self.taskData.getData()}")

        self.priority = priority

    @staticmethod
    def ReplyDanmu(
        danmu: LiveMessage[DanmuMessageData],
    ) -> "Task[LiveMessage[DanmuMessageData]]":
        return Task(TaskType.ReplyDanmu, DanmuTaskData(danmu), 1)

    def getTaskTitle(self) -> str:
        if self.taskType == TaskType.ReplyDanmu:
            return "回复弹幕任务"
        return "未知任务"

    def toDisplayDict(self) -> dict:
        return {
            "id": self.id,
            "taskType": self.taskType.value,
            "priority": self.priority,
            "taskTitle": self.getTaskTitle(),
            "taskData": self.taskData.getData(),
            "taskDetail": self,
        }
