import threading
from fastapi import Depends, FastAPI
import uvicorn
from base_component.Closer import getCloser
from base_component.Logger import BLogger, getLogger
from Birespi import biRespiHolder, getBirespi
from model.JsonDict import JsonDict
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from fastapi.responses import FileResponse, HTMLResponse
from config import BiRespiConfig, birespiConfigHolder, getConfig
from uvicorn.config import LOGGING_CONFIG

from value.ComponentConfigKey import ComponentConfigKey
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import aiohttp
import io


class BirespiBackendConfig:
    username: str = "admin"
    password: str = "admin"
    port: int = 8000
    allowNoLocalhost: bool = False

    def __init__(self, dict: dict) -> None:

        self.username = dict.get("username", "admin")
        self.password = dict.get("password", "admin")
        self.port = dict.get("port", 8000)
        self.allowNoLocalhost = dict.get("allowNoLocalhost", False)


class BirespiApi:
    api = FastAPI()

    def __init__(self) -> None:
        pass

    def start(self) -> "BirespiApi":
        # # 增加FileHandler
        # LOGGING_CONFIG["handlers"]["default"] = {
        #     "class": "logging.FileHandler",
        #     "filename": getConfig().getLoggerConfigDict()["filename"],
        # }
        # LOGGING_CONFIG["handlers"]["access"] = {
        #     "class": "logging.FileHandler",
        #     "filename": getConfig().getLoggerConfigDict()["filename"],
        # }
        # "filename": os.path.join(
        #     f"log",
        #     f'birespi-log-{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
        # ),
        uvicorn.run(
            self.api,
            host="localhost",
            port=getConfig().getWebUiConfigDict()["port"],
            # log_level=getConfig().getLoggerConfigDict()[
            #     "log_level"
            # ],  #  "log_level": "DEBUG",
        )
        return self

    @api.get("/")
    def index() -> FileResponse:
        return FileResponse("backend/index.html")

    @api.get("/log")
    def index() -> FileResponse:
        return FileResponse("backend/log.html")

    @api.get("/config")
    def index() -> FileResponse:
        return FileResponse("backend/config.html")

    @api.get("/static/{file_path:path}")
    def static_file(file_path: str) -> FileResponse:

        return FileResponse(f"backend/static/{file_path}")

    @api.get("/api/0")
    def read_root() -> dict:
        return {"code": 0, "Hello": "World"}

    @api.get("/api/version")
    def version() -> dict:
        return {"code": 0, "version": "0.1.2"}

    @api.get("/api/test/danmu/{danmu}")
    def read_root(danmu: str) -> dict:
        getBirespi().insertDanmu(
            LiveMessage[DanmuMessageData].Danmu(fromUser="admin", content=danmu)
        )
        return {"code": 0}

    @api.get("/api/danmus")
    def getDanmus() -> dict:
        danmus: list[LiveMessage[DanmuMessageData]] = list(getBirespi().getDanmus())

        return {"code": 0, "data": {"danmus": danmus}}

    @api.get("/api/last-talk")
    def getLastTalk() -> dict:
        lastTalk = getBirespi().getLastTalk()
        if lastTalk == None or len(lastTalk) == 0 or lastTalk[0] == None:
            return {"code": 1, "data": None}
        return {
            "code": 0,
            "data": {"lastTalkDanmu": lastTalk[0], "lastTalkBirespi": lastTalk[1]},
        }

    @api.post("/api/reply/{bId}")
    async def reply(bId: str) -> dict:
        await getBirespi().replyByBid(bId)
        return {"code": 0}

    @api.get("/api/logs")
    def getLogs() -> dict:
        return {"code": 0, "data": {"logs": getLogger().getLogFiles()}}

    @api.get("/api/log/{logFilename}")
    def getLog(logFilename: str) -> dict:
        return {"code": 0, "data": {"log": getLogger().getLog(logFilename)}}

    @api.get("/api/live-room-info")
    def getLiveRoomInfo() -> dict:
        return {"code": 0, "data": getBirespi().getLiveRoomInfo()}

    @api.get("/api/config/component-keys")
    def getComponentKeys() -> dict:
        return {"code": 0, "data": {"componentKeys": getConfig().getComponentKeys()}}

    @api.get("/api/config/component/{componentKey}/sub-types")
    def getComponentSubTypes(componentKey: str) -> dict:
        return {
            "code": 0,
            "data": {
                "componentSubTypes": getConfig().getComponentSubTypes(componentKey),
                "componentCurrentSubType": getConfig().getComponentCurrentType(
                    componentKey
                ),
            },
        }

    @api.get("/api/config/component/{componentKey}/subtype/{subtype}")
    def getComponentSubtypeConfig(componentKey: str, subtype: str) -> dict:
        return {
            "code": 0,
            "data": {
                "componentConfig": getConfig().getComponentSubtypeConfig(
                    componentKey, subtype
                ),
            },
        }

    @api.get("/api/config")
    def getConfig() -> dict:
        componentKeys = getConfig().getComponentKeys()
        config = {}

        for componentKey in componentKeys:
            currentSubType: str = getConfig().getComponentCurrentType(
                componentKey.value
            )
            subTypes: list[str] = getConfig().getComponentSubTypes(componentKey.value)

            config[componentKey] = {
                "componentSubTypes": subTypes,
                "componentCurrentSubType": currentSubType,
                "componentConfig": getConfig().getCurrentComponentConfig(
                    componentKey.value
                ),
            }

        return {
            "code": 0,
            "data": {"config": config, "componentKeys": componentKeys},
        }

    @api.post("/api/config/component/{componentKeyStr}/subtype/{subtype}")
    def setComponentConfig(componentKeyStr: str, subtype: str, config: Dict) -> dict:
        print("componentKey", componentKeyStr)
        print("subtype", subtype)
        print("config", config)
        componentKey = ComponentConfigKey.fromStr(componentKeyStr)
        getConfig().setComponentConfig(componentKey, subtype, config["config"])

        if (
            not (subtype == "-1")
            and not len(getConfig().getComponentSubTypes(componentKeyStr)) == 0
        ):
            getConfig().setComponentType(componentKey, subtype)

        getConfig().saveJsonConfig()
        return {"code": 0}

    @api.get("/proxy/")
    async def proxy_image(url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status, detail="Failed to download image"
                    )
                img_bytes = await response.read()
                return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")


class BirespiBackend:
    api: BirespiApi = None

    def __init__(self) -> None:
        self.api = BirespiApi()

    def start(self):
        backendThread = threading.Thread(target=self.api.start)
        backendThread.setDaemon(True)
        backendThread.start()


class BirespiBackendHolder:
    birespiBackend: BirespiBackend = None

    def set(self, birespiBackend: BirespiBackend):
        self.birespiBackend = birespiBackend

    def get(self) -> BirespiBackend:
        return self.birespiBackend


birespiBackendHolder = BirespiBackendHolder()
