import threading
from fastapi import Depends, FastAPI
from Birespi import Birespi
import uvicorn
from model.LiveEventMessage import DanmuMessageData, LiveMessage
from system import Context


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
    
    @api.get("/0")
    def read_root():
        return {"Hello": "World"}

    @api.get("/version")
    def version():
        return {"version": "0.1.2"}

    @api.get("/test/danmu/{danmu}")
    def read_root(danmu: str):

        Context.getBirespi().insertDanmu(
            LiveMessage[DanmuMessageData].Danmu(from_user="admin", content=danmu)
        )

        return {"Hello": "World"}


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
