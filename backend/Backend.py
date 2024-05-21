import threading
from fastapi import Depends, FastAPI
import uvicorn
from base_component.Closer import getCloser
from base_component.Logger import BLogger, getLogger
from Birespi import biRespiHolder, getBirespi
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from fastapi.responses import FileResponse, HTMLResponse
from config import BiRespiConfig, birespiConfigHolder, getConfig
from uvicorn.config import LOGGING_CONFIG


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
        # 增加FileHandler
        LOGGING_CONFIG["handlers"]["default"] = {
            "class": "logging.FileHandler",
            "filename": getConfig().getLoggerConfigDict()["filename"],
        }
        LOGGING_CONFIG["handlers"]["access"] = {
            "class": "logging.FileHandler",
            "filename": getConfig().getLoggerConfigDict()["filename"],
        }
        # "filename": os.path.join(
        #     f"log",
        #     f'birespi-log-{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
        # ),
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

        return {"code": 0, "Hello": "World"}

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

    @api.get("/api/logs")
    def getLogs() -> dict:
        return {"code": 0, "data": {"logs": getLogger().getLogFiles()}}

    @api.get("/api/log/{logFilename}")
    def getLog(logFilename: str) -> dict:
        return {"code": 0, "data": {"log": getLogger().getLog(logFilename)}}


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
