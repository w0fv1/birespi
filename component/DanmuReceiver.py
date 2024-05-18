import asyncio
from typing import Callable
import time

from base_component.BiliClient import BiliClient
from component.BaseConfig import BaseConfig
from model.LiveEventMessage import DanmuMessageData, LiveMessage


class BaseDanmuReceiver:
    def onReceiveDanmu(self, process: Callable[[LiveMessage[DanmuMessageData]], None]):
        raise NotImplementedError

    async def startReceive(
        self, process: Callable[[LiveMessage[DanmuMessageData]], None]
    ):
        raise NotImplementedError


class BiliOpenDanmuReceiverConfig(BaseConfig):
    idCode: str
    appId: str
    key: str
    secret: str
    host: str
    onRecvDanmu: Callable[[LiveMessage[DanmuMessageData]], None]

    def __init__(self, idCode: str, appId: str, key: str, secret: str, host: str):
        self.idCode = idCode
        self.appId = appId
        self.key = key
        self.secret = secret
        self.host = host

    @staticmethod
    def fromJson(json):
        return BiliOpenDanmuReceiverConfig(
            idCode=json["idCode"],
            appId=json["appId"],
            key=json["key"],
            secret=json["secret"],
            host=json["host"],
        )


class BiliOpenDanmuReceiver:

    biliClient: BiliClient
    config: BiliOpenDanmuReceiverConfig

    def __init__(self, configDict: dict):
        self.config = BiliOpenDanmuReceiverConfig.fromJson(configDict)
        self.biliClient = BiliClient(
            idCode=self.config.idCode,
            appId=self.config.appId,
            key=self.config.key,
            secret=self.config.secret,
            host=self.config.host,
        )

    def onReceive(self, process: Callable[[LiveMessage[DanmuMessageData]], None]):
        self.onRecvDanmu = process
        self.biliClient.onRecvDanmu = self.onRecvDanmu

    def startReceive(self):
        self.biliClient.run()
