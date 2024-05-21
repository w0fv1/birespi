import asyncio
from collections import deque
import threading
from typing import Optional
from base_component.Logger import getLogger
from config import getConfig
from model.Talk import Talk
from util.Queue import FastConsumptionQueue
from model.LiveEventMessage import LiveMessage, DanmuMessageData
from system.ComponentManager import ComponentManager


class Birespi:
    componentManager: ComponentManager = ComponentManager()
    danmuQueue = FastConsumptionQueue[LiveMessage[DanmuMessageData]]()
    danmuDisplayqueue: deque[LiveMessage[DanmuMessageData]] = deque()
    lastTalk: tuple[Talk, Talk] = (None, None)

    def __init__(self) -> None:
        self.componentManager.loadComponents(getConfig().birespiConfig)
        self.componentManager.LiveEventReceiver.onReceive(self.process)

    def start(self) -> "Birespi":
        thread = threading.Thread(target=self.startReceive)
        thread.start()
        asyncio_thread = threading.Thread(target=self.startWaitResponse)
        asyncio_thread.start()
        return self

    def process(self, danmu: LiveMessage[DanmuMessageData]):
        self.insertDanmu(danmu)

    async def waitResponse(self):
        while True:
            danmu: Optional[LiveMessage[DanmuMessageData]] = self.danmuQueue.pop()
            if danmu == None:
                # getLogger().logInfo(f"等待弹幕....")
                await asyncio.sleep(1)
                continue
            getLogger().logInfo(f"接受一条弹幕: {danmu.data.content}")
            await self.replyDanmu(danmu)

            await asyncio.sleep(0.1)

    async def replyDanmu(self, danmu: LiveMessage[DanmuMessageData]):
        answer: str = await self.componentManager.chatter.answer(
            danmu.fromUser + "说:" + danmu.data.content
        )
        self.setLastTalk(danmu, answer)
        sound = await self.componentManager.speaker.speak(answer)
        self.componentManager.player.play(sound)

    async def replyByBid(self, bId: str):
        danmu: LiveMessage[DanmuMessageData] = None
        for d in self.danmuDisplayqueue:
            if d.bId == bId:
                danmu = d
                break
        await self.replyDanmu(danmu)

    def startWaitResponse(self):
        asyncio.run(self.waitResponse())

    def startReceive(self):
        asyncio.run(self.componentManager.LiveEventReceiver.startReceive())

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
