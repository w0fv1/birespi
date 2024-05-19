from enum import Enum

from typing import TypeVar, Generic
from pydantic import BaseModel

import uuid
import time

from model.LiveEventMessage import DanmuMessageData, LiveMessage


class Talk(BaseModel):
    fromUser: str = ""
    userAvatar: str = ""
    content: str = ""
    timestamp: float = 0.0

    def __init__(
        self,
        fromUser: str = "",
        userAvatar: str = "",
        content: str = "",
        timestamp: float = 0.0,
    ):
        if timestamp == 0.0:
            timestamp = time.time()
        super().__init__(
            fromUser=fromUser,
            userAvatar=userAvatar,
            content=content,
            timestamp=timestamp,
        )

        self.fromUser = fromUser
        self.userAvatar = userAvatar
        self.content = content
        self.timestamp = timestamp

    @staticmethod
    def fromDanmu(danmu: LiveMessage[DanmuMessageData]) -> "Talk":
        return Talk(
            fromUser=danmu.fromUser,
            userAvatar=danmu.userAvatar,
            content=danmu.data.content,
            timestamp=danmu.timestamp,
        )

    @staticmethod
    def fromBirespi(content: str) -> "Talk":
        return Talk(
            fromUser="birespi", userAvatar="", content=content, timestamp=time.time()
        )
