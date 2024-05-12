import asyncio
import threading

from typing import Optional
from util.Queue import FastConsumptionQueue
from model.Danmu import Danmu
from system.ComponentManager import ComponentManager


class Birespi:
    componentManager: ComponentManager = ComponentManager()
    fastConsumptionQueue = FastConsumptionQueue[Danmu]()

    def __init__(self, config: dict) -> None:
        self.componentManager.loadComponents(config)

    def startRespi(self) -> "Birespi":
        def process(danmu: Danmu):
            print("Receive danmu:", danmu.username, ": ", danmu.content)
            self.fastConsumptionQueue.push(danmu)

        self.componentManager.danmuReceiver.onReceive(process)

        async def response():
            while True:
                danmu: Optional[Danmu] = self.fastConsumptionQueue.pop()
                if danmu == None:
                    print("没获取到弹幕,等待...")
                    await asyncio.ensure_future(asyncio.sleep(1))
                    continue
                print("Pop danmu:", danmu)
                print(f'start respi: "{danmu.username}:{danmu.content}"')
                answer = await self.componentManager.chatter.answer(
                    danmu.username + "说:" + danmu.content
                )
                print("answer: ", answer)
                sound = await self.componentManager.speaker.speak(answer)
                print("sound: ", sound)
                self.componentManager.player.play(sound)

                await asyncio.ensure_future(asyncio.sleep(1))

        asyncio.ensure_future(response())

        # async def wishes2Everyone():
        #     while True:
        #         self.fastConsumptionQueue.push(
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

    def insertDanmu(self, danmu: Danmu):
        self.fastConsumptionQueue.push(danmu)
