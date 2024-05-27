from enum import Enum
from typing import Optional
from pydantic import BaseModel

from model.LiveEventMessage import LiveMessage
from model.Task import Task
import os


class EventType(Enum):
    Danmu = "Danmu"
    Command = "ExecCommand"


class ExportEvent(BaseModel):
    eventType: EventType
    message: Optional[str]
    liveMessage: Optional[LiveMessage]
    sound: Optional[str]
    task: Task

    def __init__(
        self,
        eventType: EventType,
        message: Optional[str],
        sound: Optional[str],
        liveMessage: Optional[LiveMessage],
        task: Task,
    ):

        super().__init__(
            eventType=eventType,
            message=message,
            sound=sound,
            liveMessage=liveMessage,
            task=task,
        )

        self.eventType = eventType
        self.message = message
        self.sound = sound
        self.liveMessage = liveMessage
        self.task = task

    @staticmethod
    def Danmu(
        message: str, sound: str, liveMessage: LiveMessage, task: Task
    ) -> "ExportEvent":
        return ExportEvent(
            eventType=EventType.Danmu,
            sound=sound,
            message=message,
            liveMessage=liveMessage,
            task=task,
        )

    @staticmethod
    def Command(message: str, sound: str, task: Task) -> "ExportEvent":
        return ExportEvent(
            eventType=EventType.Command,
            sound=sound,
            message=message,
            liveMessage=None,
            task=task,
        )

    def toDict(self):

        # 判断liveMessage 是否为None
        return {
            "eventType": self.eventType.value,
            "message": self.message,
            "soundPath": self.sound,
            "sound": self.sound.split(os.sep)[-1] if self.sound else None,
            "liveMessage": self.liveMessage.model_dump() if self.liveMessage else None,
            "task": self.task.model_dump() if self.task else None,
            "taskData": self.task.taskData.model_dump(),
        }
