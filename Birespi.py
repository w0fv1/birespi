import asyncio
from collections import deque
import threading

from typing import Optional
from util.Queue import FastConsumptionQueue
from model.LiveEventMessage import LiveMessage, DanmuMessageData
from system.ComponentManager import ComponentManager


class Birespi:
    componentManager: ComponentManager = ComponentManager()
    danmuQueue = FastConsumptionQueue[LiveMessage[DanmuMessageData]]()
    danmuDisplayqueue: deque[LiveMessage[DanmuMessageData]] = deque()

    def __init__(self, config: dict) -> None:
        self.componentManager.loadComponents(config)

    def startRespi(self) -> "Birespi":
        def process(danmu: LiveMessage[DanmuMessageData]):
            print("Receive danmu:", danmu.from_user, ": ", danmu.data.content)
            self.insertDanmu(danmu)

        self.componentManager.danmuReceiver.onReceive(process)

        async def response():
            while True:
                danmu: Optional[LiveMessage[DanmuMessageData]] = self.danmuQueue.pop()
                if danmu == None:
                    print("没获取到弹幕,等待...")
                    await asyncio.ensure_future(asyncio.sleep(1))
                    continue
                print("Pop danmu:", danmu)
                print(f'start respi: "{danmu.from_user}:{danmu.data.content}"')
                answer = await self.componentManager.chatter.answer(
                    danmu.from_user + "说:" + danmu.data.content
                )
                print("answer: ", answer)
                sound = await self.componentManager.speaker.speak(answer)
                print("sound: ", sound)
                self.componentManager.player.play(sound)

                await asyncio.ensure_future(asyncio.sleep(1))

        asyncio.ensure_future(response())

        # async def wishes2Everyone():
        #     while True:
        #         self.danmuQueue.push(
        #             Danmu(
        #                 "w0fv1-dev",
        #                 "请你祝福直播间的所有人,祝福他们的事业和生活, 祝福他们的家人和朋友, 祝福他们的爱情和婚姻, 祝福他们的健康和快乐。",
        #             )
        #         )
        #         await asyncio.sleep(10)

        # asyncio.create_task(wishes2Everyone())

        self.componentManager.danmuReceiver.startReceive()
        print("start Birespi startRespi")

        print("start Birespi startRespi")
        return self

    def insertDanmu(self, danmu: LiveMessage[DanmuMessageData]):
        self.danmuQueue.push(danmu)
        self.danmuDisplayqueue.append(danmu)
        if len(self.danmuDisplayqueue) > 100:
            self.danmuDisplayqueue.popleft()
        

    def getDanmus(self)->deque[LiveMessage[DanmuMessageData]]:
        return self.danmuDisplayqueue
