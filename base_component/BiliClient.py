import asyncio
import json
from typing import Callable
import websocket
from websocket import WebSocketApp
import requests
import time
import hashlib
import hmac
import random
from hashlib import sha256
import struct
import zlib
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from aiohttp import ClientSession
import rel


class Proto:
    def __init__(self):
        self.packetLen = 0
        self.headerLen = 16
        self.ver = 0
        self.op = 0
        self.seq = 0
        self.body = ""
        self.maxBody = 2048

    def pack(self):
        self.packetLen = len(self.body) + self.headerLen
        buf = struct.pack(">i", self.packetLen)
        buf += struct.pack(">h", self.headerLen)
        buf += struct.pack(">h", self.ver)
        buf += struct.pack(">i", self.op)
        buf += struct.pack(">i", self.seq)
        buf += self.body.encode()
        return buf

    def unpack(self, buf) -> str:
        if len(buf) < self.headerLen:

            return
        self.packetLen = struct.unpack(">i", buf[0:4])[0]
        self.headerLen = struct.unpack(">h", buf[4:6])[0]
        self.ver = struct.unpack(">h", buf[6:8])[0]
        self.op = struct.unpack(">i", buf[8:12])[0]
        self.seq = struct.unpack(">i", buf[12:16])[0]
        if self.packetLen < 0 or self.packetLen > self.maxBody:
            print(
                "包体长不对",
                "self.packetLen:",
                self.packetLen,
                " self.maxBody:",
                self.maxBody,
            )
            return "-1:包体长不对"
        if self.headerLen != self.headerLen:

            return "-1:包头长度不对"
        bodyLen = self.packetLen - self.headerLen
        self.body = buf[16 : self.packetLen]
        if bodyLen <= 0:
            return "-1:包体长度不对"
        if self.ver == 0:
            # 这里做回调
            return self.body.decode("utf-8")
        else:
            return "-1:协议版本不对"


# 该示例仅为demo，如需使用在生产环境需要自行按需调整


class BiliClient:

    idCode: str = ""
    appId: int = ""
    key: str = ""
    secret: str = ""
    host: str = ""
    gameId: str = ""
    onRecv: Callable[[dict], None] = None
    websocket: WebSocketApp = None
    aioHttpSession: ClientSession = None
    websocketInfo: dict = {}
    addr: str = ""
    authBody: str = ""
    roomId: str = ""
    gameId: str = ""

    def __init__(self, idCode, appId, key, secret, host):
        self.idCode = idCode
        self.appId = appId
        self.key = key
        self.secret = secret
        self.host = host
        self.gameId = ""
        self.aioHttpSession = None
        websocket.enableTrace(False)
        self.websocket = None

    async def run(self):
        
        self.aioHttpSession = ClientSession()
        await self.connect()
        await self.heartBeat()
        await self.appheartBeat()
        while True:
            await asyncio.sleep(0.1)

    async def reRun(self):
        try:
            self.websocket.close()
            self.__exit__(None, None, None)
        except:
            pass
        await self.run()

    async def connect(self):
        def onMessage(ws, message):
            resp = Proto()
            result = resp.unpack(message)
            result = result.replace(" ", "")
            if result.startswith("-1"):
                return
            if result == "":
                return
            if "{" not in result:
                return
            message = json.loads(result)
            if self.onRecv:
                self.onRecv(message)

        def onOpen(ws):
            print("open")

        self.websocketInfo = await self.getWebsocketInfo()
        self.websocket = WebSocketApp(
            self.addr,
            on_open=onOpen,
            on_message=onMessage,
        )

        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.websocket.run_forever)
        await asyncio.sleep(2)
        self.auth()
        websocket._logging
        return websocket

    def auth(self):
        req = Proto()
        req.body = self.authBody
        req.op = 7
        self.websocket.send(req.pack())

    def signHeaderMap(self, params) -> dict:
        ts = time.time()
        nonce = random.randint(1, 100000) + time.time()
        md5 = hashlib.md5()
        md5.update(params.encode())
        md5data = md5.hexdigest()
        headerMap = {
            "x-bili-timestamp": str(int(ts)),
            "x-bili-signature-method": "HMAC-SHA256",
            "x-bili-signature-nonce": str(nonce),
            "x-bili-accesskeyid": self.key,
            "x-bili-signature-version": "1.0",
            "x-bili-content-md5": md5data,
        }

        headerStr = "\n".join(f"{k}:{v}" for k, v in sorted(headerMap.items())).rstrip(
            "\n"
        )
        appsecret = self.secret.encode()
        data = headerStr.encode()
        signature = hmac.new(appsecret, data, digestmod=sha256).hexdigest()
        headerMap["Authorization"] = signature
        headerMap["Content-Type"] = "application/json"
        headerMap["Accept"] = "application/json"
        return headerMap

    async def getWebsocketInfo(self):
        postUrl: str = f"{self.host}/v2/app/start"
        params: str = f'{{"code":"{self.idCode}","app_id":{self.appId}}}'
        headerMap = self.signHeaderMap(params)
        async with self.aioHttpSession.post(
            url=postUrl, headers=headerMap, data=params
        ) as response:
            liveInfo = await response.json()
        if liveInfo == None:
            print("获取直播信息失败")
            return
        self.addr = str(liveInfo["data"]["websocket_info"]["wss_link"][0])
        self.authBody = str(liveInfo["data"]["websocket_info"]["auth_body"])
        self.gameId = str(liveInfo["data"]["game_info"]["game_id"])
        self.roomId = str(liveInfo["data"]["anchor_info"]["room_id"])
        return liveInfo

    async def heartBeat(self):
        print("heartBeat start")
        while True:
            try:
                await asyncio.sleep(20)
                print("heartBeat")
                req = Proto()
                req.op = 2
                self.websocket.send(req.pack())
            except Exception as e:
                print(f"heartBeat error: {e}")

    async def appheartBeat(self):
        print("appheartBeat start")
        while True:
            try:

                await asyncio.sleep(20)
                print("appheartBeat")
                postUrl = f"{self.host}/v2/app/heartbeat"
                params = f'{{"game_id":"{self.gameId}"}}'
                headerMap = self.signHeaderMap(params)
                async with self.aioHttpSession.post(
                    url=postUrl, headers=headerMap, data=params, verify_ssl=False
                ) as response:
                    data = await response.json()
            except Exception as e:
                print(f"appheartBeat error: {e}")

    def __enter__(self):
        pass

    def __exit__(self, type, value, trace):
        postUrl = f"{self.host}/v2/app/end"
        params = f'{{"game_id":"{self.gameId}","app_id":{self.appId}}}'
        headerMap = self.sign(params)
        requests.post(url=postUrl, headers=headerMap, data=params, verify=False)

        asyncio.create_task(self.aioHttpSession.close())
