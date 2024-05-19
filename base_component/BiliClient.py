import asyncio
import json
from typing import Callable
import websockets
import requests
import time
import hashlib
import hmac
import random
from hashlib import sha256
import struct
import zlib
from model.LiveEventMessage import DanmuMessageData, LiveMessage


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
    idCode: str
    appId: int
    key: str
    secret: str
    host: str
    gameId: str
    onRecvDanmu: Callable[[LiveMessage[DanmuMessageData]], None]

    def __init__(self, idCode, appId, key, secret, host):
        self.idCode = idCode
        self.appId = appId
        self.key = key
        self.secret = secret
        self.host = host
        self.gameId = ""
        pass

    websocket = None

    async def reRun(self):
        
        try:
            await self.websocket.close()
            self.__exit__(None, None, None)
        except:
            pass
        self.run()
        pass

    # 事件循环
    def run(self):
        loop = asyncio.get_event_loop()
        # 建立连接
        websocket = loop.run_until_complete(self.connect())
        tasks = [
            # 读取信息
            asyncio.ensure_future(self.recvLoop(websocket)),
            # 发送心跳
            asyncio.ensure_future(self.heartBeat(websocket)),
            # 发送游戏心跳
            asyncio.ensure_future(self.appheartBeat()),
        ]
        loop.run_until_complete(asyncio.gather(*tasks))

    # http的签名
    def sign(self, params):
        key = self.key
        secret = self.secret
        md5 = hashlib.md5()
        md5.update(params.encode())
        ts = time.time()
        nonce = random.randint(1, 100000) + time.time()
        md5data = md5.hexdigest()
        headerMap = {
            "x-bili-timestamp": str(int(ts)),
            "x-bili-signature-method": "HMAC-SHA256",
            "x-bili-signature-nonce": str(nonce),
            "x-bili-accesskeyid": key,
            "x-bili-signature-version": "1.0",
            "x-bili-content-md5": md5data,
        }

        headerList = sorted(headerMap)
        headerStr = ""

        for key in headerList:
            headerStr = headerStr + key + ":" + str(headerMap[key]) + "\n"
        headerStr = headerStr.rstrip("\n")

        appsecret = secret.encode()
        data = headerStr.encode()
        signature = hmac.new(appsecret, data, digestmod=sha256).hexdigest()
        headerMap["Authorization"] = signature
        headerMap["Content-Type"] = "application/json"
        headerMap["Accept"] = "application/json"
        return headerMap

    # 获取长连信息
    def getWebsocketInfo(self):
        # 开启应用
        postUrl = "%s/v2/app/start" % self.host
        params = '{"code":"%s","app_id":%d}' % (self.idCode, self.appId)
        headerMap = self.sign(params)
        r = requests.post(url=postUrl, headers=headerMap, data=params, verify=False)
        live_info = json.loads(r.content)
        self.gameId = str(live_info["data"]["game_info"]["game_id"])

        # 获取长连地址和鉴权体
        return str(live_info["data"]["websocket_info"]["wss_link"][0]), str(
            live_info["data"]["websocket_info"]["auth_body"]
        )

    # 发送游戏心跳
    async def appheartBeat(self):
        while True:
            await asyncio.ensure_future(asyncio.sleep(20))
            postUrl = "%s/v2/app/heartbeat" % self.host
            params = '{"game_id":"%s"}' % (self.gameId)
            headerMap = self.sign(params)
            try:
                r = requests.post(
                    url=postUrl, headers=headerMap, data=params, verify=False
                )
                data = json.loads(r.content)
            except Exception as e:
                
                await self.reRun()

    # 发送鉴权信息
    async def auth(self, websocket, authBody):
        req = Proto()
        req.body = authBody
        req.op = 7
        await websocket.send(req.pack())
        buf = await websocket.recv()
        resp = Proto()
        resp.unpack(buf)
        respBody = json.loads(resp.body)
        if respBody["code"] != 0:
            pass
        else:
            pass

    # 发送心跳
    async def heartBeat(self, websocket):
        while True:
            await asyncio.ensure_future(asyncio.sleep(20))
            req = Proto()
            req.op = 2
            await websocket.send(req.pack())

    # 读取信息
    async def recvLoop(self, websocket):
        while True:
            recvBuf = await websocket.recv()
            resp = Proto()
            result = resp.unpack(recvBuf)
            # 去除空格
            result = result.replace(" ", "")
            if result.startswith("-1"):
                
                continue
            if result == "":
                
                continue
            if "{" not in result:
                
                continue

            
            message = json.loads(result)
            if message["cmd"] == "LIVE_OPEN_PLATFORM_DM":
                
                danmu = LiveMessage.Danmu(
                    fromUser=message["data"]["uname"],
                    content=message["data"]["msg"],
                )
                self.onRecvDanmu(danmu)

    # 建立连接
    async def connect(self):
        addr, authBody = self.getWebsocketInfo()
        websocket = await websockets.connect(addr)
        # 鉴权
        await self.auth(websocket, authBody)
        return websocket

    def __enter__(self):
        pass

    def __exit__(self, type, value, trace):
        # 关闭应用
        postUrl = "%s/v2/app/end" % self.host
        params = '{"game_id":"%s","app_id":%d}' % (self.gameId, self.appId)
        headerMap = self.sign(params)
        r = requests.post(url=postUrl, headers=headerMap, data=params, verify=False)
