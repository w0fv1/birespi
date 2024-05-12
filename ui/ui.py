from fastapi import FastAPI

from Birespi import Birespi

import uvicorn


class BirespiUI:
    api = FastAPI()
    biresp = None

    def __init__(self, biresp: Birespi) -> None:
        self.biresp = biresp

    def startUi(self) -> "BirespiUI":

        uvicorn.run(self.api)

        return self

    @api.get("/")
    def read_root():
        return {"Hello": "World"}
