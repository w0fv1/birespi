import datetime
import signal
import threading
import time
from fastapi import Depends, FastAPI, File, UploadFile
import uvicorn
from base_component.Closer import getCloser
from system.Logger import BLogger, getLogger
from system.Birespi import biRespiHolder, getBirespi
from model.JsonDict import JsonDict
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from fastapi.responses import FileResponse, HTMLResponse
from system.Config import BiRespiConfig, birespiConfigHolder, getConfig
from uvicorn.config import LOGGING_CONFIG

from value.ComponentConfigKey import ComponentConfigKey
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import aiohttp
import io
import subprocess
from fastapi.middleware.cors import CORSMiddleware


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
    server_process = None
    api = FastAPI()

    def __init__(self) -> None:
        pass

    def restart(self):
        getLogger().logInfo("Restarting backend server")
        if self.server_process != None:
            getLogger().logInfo("Killing backend server")
            self.server_process.send_signal(signal.SIGINT)
            time.sleep(1)
            self.server_process.terminate()
            time.sleep(1)
            self.server_process.kill()
            getLogger().logInfo("Backend server killed")
        getLogger().logInfo("Starting backend server")
        self.start()

    def start(self) -> "BirespiApi":
        LOGGING_CONFIG["handlers"]["file-default"] = {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": getConfig()
            .getLoggerConfigDict()["filename"]
            .replace("%(today)s", datetime.datetime.now().strftime("%Y-%m-%d")),
        }
        LOGGING_CONFIG["handlers"]["file-access"] = {
            "formatter": "access",
            "class": "logging.FileHandler",
            "filename": getConfig()
            .getLoggerConfigDict()["filename"]
            .replace("%(today)s", datetime.datetime.now().strftime("%Y-%m-%d")),
        }
        LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"] = ["default", "file-default"]
        LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"] = [
            "access",
            "file-access",
        ]
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        uvicorn.run(
            self.api,
            host="localhost",
            port=getConfig().getWebUiConfigDict()["port"],
            log_level=getConfig().getLoggerConfigDict()[
                "log_level"
            ],  #  "log_level": "DEBUG",
        )

        return self

    @api.get("/")
    def index() -> FileResponse:
        return FileResponse("system/backend/index.html")

    @api.get("/log")
    def index() -> FileResponse:
        return FileResponse("system/backend/log.html")

    @api.get("/config")
    def index() -> FileResponse:
        return FileResponse("system/backend/config.html")

    @api.get("/data")
    def index() -> FileResponse:
        return FileResponse("system/backend/data.html")

    @api.get("/task")
    def index() -> FileResponse:
        return FileResponse("system/backend/task.html")

    @api.get("/static/{file_path:path}")
    def static_file(file_path: str) -> FileResponse:
        return FileResponse(f"system/backend/static/{file_path}")

    @api.get("/sound/{filename}")
    async def getSound(filename: str):
        return FileResponse(f"sound/{filename}")

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

    @api.get("/api/datas")
    def getDatas() -> dict:
        return {"code": 0, "data": {"datas": getBirespi().getDataFiles()}}

    @api.get("/api/data/{filename}")
    def getData(filename: str) -> dict:
        return {"code": 0, "data": {"data": getBirespi().getData(filename)}}

    @api.put("/api/data/{filename}")
    async def putData(filename: str, body: dict) -> dict:
        getLogger().logInfo(f"Updating data {filename} {body}")
        getBirespi().uploadData(filename, body["content"])
        return {"code": 0}

    @api.post("/api/data")
    async def upload_file(file: UploadFile = File(...)):
        contentByte = await file.read()
        content = contentByte.decode("utf-8")
        getBirespi().uploadData(file.filename, content)
        return {"code": 0, "dara": {"filename": file.filename, "content": content}}

    @api.delete("/api/data/{filename}")
    async def deleteData(filename: str) -> dict:
        getBirespi().deleteData(filename)
        return {"code": 0}

    # 表单上传一个文件
    @api.post("/api/upload")
    async def upload_file(file: UploadFile = File(...)):
        content = await file.read()
        return {"filename": file.filename, "content": content}

    @api.get("/api/live-room-info")
    async def getLiveRoomInfo() -> dict:
        return {"code": 0, "data": getBirespi().getLiveRoomInfo()}

    @api.get("/api/birespi-info")
    async def getBiRespiInfo() -> dict:
        return {
            "code": 0,
            "data": {
                "exportContentedWebsocketCount": getBirespi().getExportContentedWebsocketCount(),
                "taskInfo": getBirespi().getTaskInfo(),
            },
        }

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
                "enable": getConfig().isComponentEnable(componentKey.value),
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
        componentKey = ComponentConfigKey.fromStr(componentKeyStr)
        getConfig().setComponentConfig(componentKey, subtype, config["config"])

        if (
            not (subtype == "-1")
            and not len(getConfig().getComponentSubTypes(componentKeyStr)) == 0
        ):
            getConfig().setComponentType(componentKey, subtype)

        getBirespi().reloadComponent(componentKey)
        if componentKey == ComponentConfigKey.WebUi:
            getBirespiBackend().api.restart()
        getConfig().saveJsonConfig()
        return {"code": 0}

    @api.put("/api/config/component/{componentKeyStr}/enable")
    def enableComponent(componentKeyStr: str) -> dict:

        getConfig().enableComponent(componentKeyStr)
        componentKeys = getConfig().getComponentKeys()
        config = {}

        for componentKey in componentKeys:
            currentSubType: str = getConfig().getComponentCurrentType(
                componentKey.value
            )
            subTypes: list[str] = getConfig().getComponentSubTypes(componentKey.value)

            config[componentKey] = {
                "componentSubTypes": subTypes,
                "enable": getConfig().isComponentEnable(componentKey.value),
                "componentCurrentSubType": currentSubType,
                "componentConfig": getConfig().getCurrentComponentConfig(
                    componentKey.value
                ),
            }

        return {
            "code": 0,
            "data": {"config": config, "componentKeys": componentKeys},
        }

    @api.get("/proxy/")
    async def proxy_image(url: str):
        if not url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid URL")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status, detail="Failed to download image"
                    )
                img_bytes = await response.read()
                return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")

    @api.get("/api/task/info")
    def getTaskManagerInfo() -> dict:
        currentTask = getBirespi().getCurrentTask()
        currentTaskDict = None
        if currentTask != None:
            currentTaskDict = currentTask.toDisplayDict()

        return {
            "code": 0,
            "data": {
                "tasks": map(lambda x: x.toDisplayDict(), getBirespi().getAllTasks()),
                "currentTask": currentTaskDict,
                "info": getBirespi().getTaskManagerInfo(),
            },
        }

    @api.put("/api/task/pause/{pause}")
    def pauseTaskManager(pause: bool) -> dict:
        getBirespi().setTaskManagerPaused(pause)
        return {
            "code": 0,
            "data": {
                "info": getBirespi().getTaskManagerInfo(),
            },
        }

    @api.post("/api/task/command")
    def addCommandTask(command: dict) -> dict:
        getBirespi().addCommandTask(command["command"])
        return {"code": 0}


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


def getBirespiBackend() -> BirespiBackend:
    return birespiBackendHolder.get()
