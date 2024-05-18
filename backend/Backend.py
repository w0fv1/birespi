import threading
from fastapi import Depends, FastAPI
from Birespi import Birespi
import uvicorn
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from system import Context
from fastapi.responses import FileResponse, HTMLResponse


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
    config: BirespiBackendConfig = None

    def __init__(self, config: dict) -> None:
        self.config = BirespiBackendConfig(config)
        print("BirespiApi init")

    def start(self) -> "BirespiApi":
        uvicorn.run(self.api, host="localhost", port=self.config.port)
        return self

    @api.get("/")
    def index() -> FileResponse:
        return FileResponse("backend/index.html")

    @api.get("/static/{file_path:path}")
    def static_file(file_path: str) -> FileResponse:
        print(f"static_file {file_path}")
        return FileResponse(f"backend/static/{file_path}")

    @api.get("/api/0")
    def read_root() -> dict:
        return {"Hello": "World"}

    @api.get("/api/version")
    def version() -> dict:
        return {"version": "0.1.2"}

    @api.get("/api/test/danmu/{danmu}")
    def read_root(danmu: str) -> dict:

        Context.getBirespi().insertDanmu(
            LiveMessage[DanmuMessageData].Danmu(from_user="admin", content=danmu)
        )

        return {"Hello": "World"}

    @api.get("/api/danmus")
    def getDanmus() -> dict:
        danmuList: list[LiveMessage[DanmuMessageData]] = list(
            Context.getBirespi().getDanmus()
        )
        print("danmuList", danmuList)
        return {"code": 0, "data": {"danmus": danmuList}}


class BirespiBackend:
    config: BirespiBackendConfig = None
    api: BirespiApi = None

    def __init__(self, config: dict) -> None:
        self.config = BirespiBackendConfig(config)
        self.api = BirespiApi(config)

    def start(self):
        uiThread = threading.Thread(target=self.api.start)
        uiThread.start()
        print("BirespiUI start")
