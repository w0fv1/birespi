from fastapi import Depends, FastAPI
from Birespi import Birespi
import uvicorn
from model.Danmu import Danmu
from system import Context

class BirespiUIConfig:
    username: str = "admin"
    password: str = "admin"
    port: int = 8000
    allowNoLocalhost: bool = False

    def __init__(self, dict: dict) -> None:

        self.username = dict.get("username", "admin")
        self.password = dict.get("password", "admin")
        self.port = dict.get("port", 8000)
        self.allowNoLocalhost = dict.get("allowNoLocalhost", False)


class BirespiAPI:
    api = FastAPI()
    config: BirespiUIConfig = None

    def __init__(self, config: dict) -> None:
        self.config = BirespiUIConfig(config)
        print("BirespiAPI init")

    def start(self) -> "BirespiUI":
        uvicorn.run(self.api, host="localhost", port=self.config.port)
        return self

    @api.get("/0")
    def read_root():
        return {"Hello": "World"}

    @api.get("/test/danmu/{danmu}")
    def read_root(danmu: str):

        Context.getBirespi().insertDanmu(Danmu("admin", danmu))

        return {"Hello": "World"}


class BirespiUI:
    config: BirespiUIConfig = None
    api: BirespiAPI = None

    def __init__(self,  config: dict) -> None:
        self.config = BirespiUIConfig(config)
        self.api = BirespiAPI(config)
        
    
    def start(self):
        self.api.start()
        print("BirespiUI start")