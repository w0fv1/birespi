from enum import Enum

from typing import TypeVar, Generic
from pydantic import BaseModel


class LiveEvent(Enum):
    Start = "start"
    End = "end"
    Danmu = "danmu"
    Follow = "follow"


class BaseLiveMessageData(BaseModel):
    pass


T = TypeVar("T", bound=BaseLiveMessageData)


class DanmuMessageData(BaseLiveMessageData):
    content: str = ""

    def __init__(self, content: str):
        super().__init__(content=content)
        self.content = content

    def __str__(self) -> str:
        return f"DanmuMessageData(content={self.content})"


class LiveMessage(BaseModel, Generic[T]):
    event: LiveEvent
    from_user: str
    data: T

    def __init__(self, event: LiveEvent, from_user: str, data: T):
        super().__init__(event=event, from_user=from_user, data=data)
        self.event = event
        self.from_user = from_user
        self.data = data

    @staticmethod
    def Danmu(from_user: str, content: str) -> "LiveMessage[DanmuMessageData]":
        return LiveMessage(LiveEvent.Danmu, from_user, DanmuMessageData(content))

    def __str__(self):
        return f"LiveMessage(event={self.event}, from_user={self.from_user}, data={self.data})"


damuLiveMessage = LiveMessage[DanmuMessageData].Danmu("user1", "hello")

print(damuLiveMessage)
