import asyncio
from collections import deque
import threading
from typing import Optional
from base_component.Logger import getLogger
from model.Talk import Talk
from util.Queue import FastConsumptionQueue
from model.LiveEventMessage import LiveMessage, DanmuMessageData
from system.ComponentManager import ComponentManager


class Birespi:
    componentManager: ComponentManager = ComponentManager()
    danmuQueue = FastConsumptionQueue[LiveMessage[DanmuMessageData]]()
    danmuDisplayqueue: deque[LiveMessage[DanmuMessageData]] = deque()
    lastTalk: tuple[Talk, Talk] = (None, None)

    def __init__(self, config: dict) -> None:
        self.componentManager.loadComponents(config)
        self.componentManager.danmuReceiver.onReceive(self.process)

    def start(self) -> "Birespi":
        thread = threading.Thread(target=self.startReceive)
        thread.start()
        asyncio_thread = threading.Thread(target=self.startWaitResponse)
        asyncio_thread.start()
        return self

    def process(self, danmu: LiveMessage[DanmuMessageData]):
        self.insertDanmu(danmu)

    async def waitResponse(self):
        print("startWait")
        while True:
            danmu: Optional[LiveMessage[DanmuMessageData]] = self.danmuQueue.pop()
            if danmu == None:
                getLogger().log_info(f"等待弹幕....")
                await asyncio.sleep(1)
                continue
            getLogger().log_info(f"接受一条弹幕: {danmu.data.content}")
            self.setLastTalk(danmu, "生成中.....")

            answer: str = await self.componentManager.chatter.answer(
                danmu.fromUser + "说:" + danmu.data.content
            )

            self.setLastTalk(danmu, answer)
            sound = await self.componentManager.speaker.speak(answer)

            self.componentManager.player.play(sound)

            await asyncio.sleep(1)

    def startWaitResponse(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.waitResponse())

    def startReceive(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.componentManager.danmuReceiver.startReceive())

    def insertDanmu(self, danmu: LiveMessage[DanmuMessageData]):
        self.danmuQueue.push(danmu)
        self.danmuDisplayqueue.append(danmu)
        if len(self.danmuDisplayqueue) > 100:
            self.danmuDisplayqueue.popleft()

    def getDanmus(self) -> deque[LiveMessage[DanmuMessageData]]:
        return self.danmuDisplayqueue

    def setLastTalk(self, talk: LiveMessage[DanmuMessageData], answer: str):
        self.lastTalk = (Talk.fromDanmu(talk), Talk.fromBirespi(answer))

    def getLastTalk(self) -> tuple[Talk, Talk]:
        return self.lastTalk


class BirespiHolder:
    birespi: Birespi = None

    def set(self, birespi: Birespi):
        self.birespi = birespi

    def get(self) -> Birespi:
        return self.birespi


biRespiHolder: BirespiHolder = BirespiHolder()


def getBirespi() -> Birespi:
    return biRespiHolder.get()
