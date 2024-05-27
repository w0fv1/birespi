#!/usr/bin/env python

import asyncio
import json
from fastapi.responses import FileResponse
import uvicorn
from websockets.server import serve
import threading
import time

from system.Logger import getLogger
from util.JsonUtil import EnumEncoder
from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware


class EventExporterConfig:
    host: str = None
    port: int = None

    def __init__(self, host: str = None, port: int = None) -> None:
        self.host = host
        self.port = port

    @staticmethod
    def fromDict(dict: dict) -> "EventExporterConfig":
        return EventExporterConfig(dict["host"], dict["port"])


class EventExporter:
    config: EventExporterConfig = None
    websocketList = []

    def __init__(self, config: dict):
        self.config = EventExporterConfig.fromDict(config)

    async def start(self):
        async with serve(self._handler, self.config.host, self.config.port):
            getLogger().logInfo(
                f"Event exporter websocket server started at {self.config.host}:{self.config.port}"
            )
            await asyncio.Future()  # run forever

    def startSoundFileApi(self):
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        @app.get("/sound/{filename}")
        async def getSound(filename: str):
            return FileResponse(f"sound/{filename}")

        uvicorn.run(app, host=self.config.host, port=self.config.port - 1)

    async def _handler(self, websocket):
        getLogger().logInfo("Websocket connected")
        self.websocketList.append(websocket)
        async for message in websocket:
            await websocket.send(message)

    async def send(self, message: dict):
        for websocket in self.websocketList:
            if websocket.open:
                await websocket.send(
                    json.dumps(message, ensure_ascii=False, cls=EnumEncoder)
                )


async def run_server(eventExporter):
    await eventExporter.start()


if __name__ == "__main__":
    config = {"host": "localhost", "port": 8765}
    eventExporter = EventExporter(config)

    server_thread = threading.Thread(
        target=asyncio.run, args=(run_server(eventExporter),)
    )
    server_thread.start()

    async def send_messages():
        while True:
            print("Sending message from main thread")
            await eventExporter.send(
                {"type": "event", "data": "Hello from main thread"}
            )
            await asyncio.sleep(1)

    # Start sending messages in the main thread's event loop
    asyncio.run(send_messages())
