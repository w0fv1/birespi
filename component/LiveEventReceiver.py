import asyncio
import json
from typing import Callable
import time

from base_component.BiliClient import BiliClient
from system.Logger import getLogger
from component.BaseConfig import BaseConfig
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from model.LiveRoomInfo import LiveRoomInfo

from bilibili_api import live, sync
from bilibili_api.login import (
    login_with_qrcode_term,
    login_with_password,
    login_with_sms,
    send_sms,
    PhoneNumber,
    Check,
)


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

    def getLiveRoomInfo(self) -> LiveRoomInfo:
        return LiveRoomInfo(
            roomId=self.biliClient.roomId,
            uname=self.biliClient.uname,
            uavatar=self.biliClient.uface,
            uid=self.biliClient.uid,
            title="",
            cover="",
            isConnected=self.biliClient.getStatus()["isConnected"],
        )


class ThirdLiveEventReceiverConfig(BaseConfig):
    username: str = ""
    password: str = ""
    roomId: int
    buvid3: str = ""

    def __init__(self, username: str, password: str, roomId: int, buvid3: str):
        self.username = username
        self.password = password
        self.roomId = roomId
        self.buvid3 = buvid3

    @staticmethod
    def fromJson(json):
        return ThirdLiveEventReceiverConfig(
            username=json["username"],
            password=json["password"],
            roomId=json["roomId"],
            buvid3=json["buvid3"],
        )


class ThirdLiveEventReceiver(BaseLiveEventReceiver):
    config: ThirdLiveEventReceiverConfig
    liveRoomInfo: LiveRoomInfo
    credential = None
    liveDanmaku: live.LiveDanmaku = None
    room: live.LiveRoom = None

    onRecvDanmu: Callable[[LiveMessage[DanmuMessageData]], None] = None

    def __init__(self, configDict: dict):
        self.config = ThirdLiveEventReceiverConfig.fromJson(configDict)

    def onReceive(self, process: Callable[[LiveMessage[DanmuMessageData]], None]):
        self.onRecvDanmu = process

    async def startReceive(self):
        self.login()
        self.credential.buvid3 = self.config.buvid3
        self.liveDanmaku = live.LiveDanmaku(
            self.config.roomId, credential=self.credential
        )
        self.room = live.LiveRoom(self.config.roomId, self.credential)

        @self.liveDanmaku.on("DANMU_MSG")
        async def on_danmaku(event):
            getLogger().logInfo(f"onReceive: {json.dumps(event,ensure_ascii=False)}")

            if self.onRecvDanmu != None:
                if event["type"] == "DANMU_MSG":
                    danmu = LiveMessage.Danmu(
                        id=event["data"]["info"][0][15]["user"]["base"]["name"]
                        + event["data"]["info"][1],
                        fromUser=event["data"]["info"][0][15]["user"]["base"]["name"],
                        userAvatar=event["data"]["info"][0][15]["user"]["base"]["face"],
                        content=event["data"]["info"][1],
                    )
                    self.onRecvDanmu(danmu)
                pass

        await self.liveDanmaku.connect()
        getLogger().logInfo("第三方弹幕链接成功")
        roomInfoDict = (await self.room.get_room_info())["room_info"]
        anchorInfoDict = (await self.room.get_room_info())["anchor_info"]
        self.liveRoomInfo = LiveRoomInfo(
            roomId=roomInfoDict["room_id"],
            uid=roomInfoDict["uid"],
            uname=anchorInfoDict["base_info"]["uname"],
            uavatar=anchorInfoDict["base_info"]["face"],
            title=roomInfoDict["title"],
            cover=roomInfoDict["cover"],
            isConnected=self.liveDanmaku.get_status() == 2,
        )
        getLogger().logInfo(f"self.liveDanmaku.get_status() {self.liveDanmaku.get_status()}")

    def getLiveRoomInfo(self) -> LiveRoomInfo:
        getLogger().logInfo(f"self.liveDanmaku.get_status() {self.liveDanmaku.get_status()}")
        return self.liveRoomInfo

    def login(self):
        c = login_with_password(self.config.username, self.config.password)
        if isinstance(c, Check):
            # 还需验证
            getLogger().logInfo("需要进行验证。请考虑使用二维码登录")

            c = login_with_qrcode_term()
            try:
                c.raise_for_no_bili_jct()  # 判断是否成功
                c.raise_for_no_sessdata()  # 判断是否成功
            except:
                getLogger().logInfo("登陆失败!请重新尝试登录。")
        getLogger().logInfo("登录成功!")
        self.credential = c
