from enum import Enum

from typing import TypeVar, Generic
from pydantic import BaseModel

import uuid
import time


class LiveEvent(Enum):
    Unknown = "unknown"
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
    bId: str = ""
    bTimestamp: float = 0.0
    id: str = ""
    timestamp: float = 0.0
    event: LiveEvent = LiveEvent.Unknown
    fromUser: str = ""
    userAvatar: str = ""
    data: T = None

    def __init__(
        self,
        event: LiveEvent,
        id: str = "",
        timestamp: str = 0.0,
        fromUser: str = "",
        userAvatar: str = "",
        data: T = None,
    ):
        if id == "":
            id = str(uuid.uuid1())
        if timestamp == 0.0:
            timestamp = time.time()

        super().__init__(
            event=event,
            id=id,
            timestamp=timestamp,
            fromUser=fromUser,
            userAvatar=userAvatar,
            data=data,
        )
        self.bId = str(uuid.uuid1()) + "-" + str(uuid.uuid4())
        self.bTimestamp = time.time()
        self.id = id
        self.timestamp = timestamp

        self.event = event
        self.fromUser = fromUser
        self.userAvatar = userAvatar
        self.data = data

    @staticmethod
    def Danmu(
        id: str = "",
        timestamp: str = 0.0,
        fromUser: str = "",
        userAvatar: str = "",
        content: str = "",
    ) -> "LiveMessage[DanmuMessageData]":
        return LiveMessage(
            LiveEvent.Danmu,
            id,
            timestamp,
            fromUser,
            userAvatar,
            DanmuMessageData(content),
        )

    def __str__(self):
        return f"LiveMessage(event={self.event}, fromUser={self.fromUser}, data={self.data})"