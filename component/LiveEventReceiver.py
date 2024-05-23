import asyncio
from typing import Callable
import time

from base_component.BiliClient import BiliClient
from base_component.Logger import getLogger
from component.BaseConfig import BaseConfig
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from model.LiveRoomInfo import LiveRoomInfo


class BaseLiveEventReceiver:
    def onReceive(self, process: Callable[[LiveMessage[DanmuMessageData]], None]):
        raise NotImplementedError

    async def startReceive(self):
        raise NotImplementedError

    def getLiveRoomInfo(self):
        raise NotImplementedError


class BiliOpenLiveEventReceiverConfig(BaseConfig):
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
        return BiliOpenLiveEventReceiverConfig(
            idCode=json["idCode"],
            appId=json["appId"],
            key=json["key"],
            secret=json["secret"],
            host=json["host"],
        )


class BiliOpenLiveEventReceiver(BaseLiveEventReceiver):

    biliClient: BiliClient
    config: BiliOpenLiveEventReceiverConfig
    liveRoomInfo: LiveRoomInfo

    def __init__(self, configDict: dict):
        self.config = BiliOpenLiveEventReceiverConfig.fromJson(configDict)
        self.biliClient = BiliClient(
            idCode=self.config.idCode,
            appId=self.config.appId,
            key=self.config.key,
            secret=self.config.secret,
            host=self.config.host,
        )

    def onReceive(self, process: Callable[[LiveMessage[DanmuMessageData]], None]):
        self.onRecvDanmu = process

        def onRecv(message: dict):
            getLogger().logInfo(f"onReceive: {message}")

            if message["cmd"] == "LIVE_OPEN_PLATFORM_DM":
                danmu = LiveMessage.Danmu(
                    id=message["data"]["msg_id"],
                    fromUser=message["data"]["uname"],
                    userAvatar=message["data"]["uface"],
                    content=message["data"]["msg"],
                )
                self.onRecvDanmu(danmu)

        self.biliClient.onRecv = onRecv

    async def startReceive(self):
        await self.biliClient.run()
        while True:
            await asyncio.sleep(0.1)

    def getLiveRoomInfo(self):
        return LiveRoomInfo(
            roomId=self.biliClient.roomId,
            uname=self.biliClient.uname,
            uavatar=self.biliClient.uface,
            uid=self.biliClient.uid,
            title="",
            cover="",
            isConnected=self.biliClient.getStatus()["isConnected"],
        )
