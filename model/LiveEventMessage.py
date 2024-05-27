from enum import Enum

import json
from typing import TypeVar, Generic
from pydantic import BaseModel

import uuid
import time

from util.JsonUtil import EnumEncoder


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
        bId = str(uuid.uuid1()) + "-" + str(uuid.uuid4())
        bTimestamp = time.time()

        super().__init__(
            bId=bId,
            bTimestamp=bTimestamp,
            event=event,
            id=id,
            timestamp=timestamp,
            fromUser=fromUser,
            userAvatar=userAvatar,
            data=data,
        )
        self.bId = bId
        self.bTimestamp = bTimestamp
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
            event=LiveEvent.Danmu,
            id=id,
            timestamp=timestamp,
            fromUser=fromUser,
            userAvatar=userAvatar,
            data=DanmuMessageData(content),
        )



    def toDict(self) -> str:

        return json.dumps({
            "bId": self.bId,
            "bTimestamp": self.bTimestamp,
            "id": self.id,
            "timestamp": self.timestamp,
            "event": self.event,
            "fromUser": self.fromUser,
            "userAvatar": self.userAvatar,
            "data": self.data.model_dump(),
        }, ensure_ascii=False, cls=EnumEncoder, indent=4)


