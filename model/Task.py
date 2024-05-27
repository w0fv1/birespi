from enum import Enum
import json
from typing import Any, Dict, TypeVar, Generic
import uuid

from pydantic import BaseModel
from model.LiveEventMessage import DanmuMessageData, LiveMessage


class TaskType(Enum):
    ReplyDanmu = "ReplyDanmu"
    ExecCommand = "ExecCommand"


T = TypeVar("T")


class TaskData(BaseModel, Generic[T]):
    def getData(self) -> T:
        pass

    def getDataDict(self) -> Dict[str, Any]:
        pass


class DanmuTaskData(TaskData[LiveMessage]):
    danmu: LiveMessage

    def __init__(self, danmu: LiveMessage[DanmuMessageData]):
        super().__init__(danmu=danmu)
        self.danmu = danmu

    def getData(self) -> LiveMessage[DanmuMessageData]:
        return self.danmu

    def getDataDict(self) -> Dict[str, Any]:
        return self.danmu.toDict()


class CommandTaskData(TaskData[str]):
    command: str

    def __init__(self, command: str):
        super().__init__(command=command)
        self.command = command

    def getData(self) -> str:
        return self.command

    def getDataDict(self) -> Dict[str, Any]:
        return {"command": self.command}


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
        self.priority = priority

    @staticmethod
    def ReplyDanmu(
        danmu: LiveMessage[DanmuMessageData],
    ) -> "Task[LiveMessage[DanmuMessageData]]":
        return Task(
            taskType=TaskType.ReplyDanmu, taskData=DanmuTaskData(danmu), priority=1
        )

    @staticmethod
    def Command(command: str) -> "Task[str]":
        return Task(
            taskType=TaskType.ExecCommand, taskData=CommandTaskData(command), priority=2
        )

    def getTaskTitle(self) -> str:
        if self.taskType == TaskType.ReplyDanmu:
            return f'回复来自{self.taskData.getData().fromUser}弹幕"{self.taskData.getData().data.content}"的任务'
        if self.taskType == TaskType.ExecCommand:
            return f"执行指令{self.taskData.getData()}的任务"
        return "未知任务"

    def toDisplayDict(self) -> dict:
        return {
            "id": self.id,
            "taskType": self.taskType.value,
            "priority": self.priority,
            "taskTitle": self.getTaskTitle(),
            "taskData": self.taskData.getData(),
            "taskDetail": self.model_dump(),
        }
