import asyncio
from typing import Optional
from component.DanmuReceiver import (
    BaseDanmuReceiver,
    BiliOpenDanmuReceiver,
)
from component.Chatter import BaseChatter
from util.Queue import FastConsumptionQueue
from component.SoundPlayer import BasePlayer
from component.Speaker import BaseSpeaker
from config import BiRespiConfig
from model.Danmu import Danmu
import threading
from threading import Lock
from system.ComponentManager import ComponentManager
import os

birespiConfig = BiRespiConfig.birespiConfig
componentManager = ComponentManager()
componentManager.loadComponents(birespiConfig)
print(birespiConfig)


async def testChatter():
    chater: BaseChatter = componentManager.buildChatter(birespiConfig["chatter"])
    result = await chater.answer("Hello")
    print(result)


async def testSpeaker():
    speaker: BaseSpeaker = componentManager.buildSpeaker(birespiConfig["speaker"])
    result = await speaker.speak("你好")
    print(result)


async def testPlayer():
    player: BasePlayer = componentManager.buildPlayer(birespiConfig["player"])
    player.config.playDelete = False
    currntPath = os.path.abspath(os.path.dirname(__file__))
    player.play(currntPath + "/lib/test.mp3")


asyncio.run(testPlayer())


async def testReply():
    chater: BaseChatter = componentManager.buildChatter(birespiConfig["chatter"])
    speaker: BaseSpeaker = componentManager.buildSpeaker(birespiConfig["speaker"])
    player = componentManager.buildPlayer(birespiConfig["player"])
    result = await chater.answer("你好")
    print(result)
    result = await speaker.speak(result)
    print(result)
    player.play(result)


async def testDanmuReceiver():
    danmuReceiver: BaseDanmuReceiver = componentManager.buildDanmuReceiver(
        birespiConfig["danmu_receiver"]
    )

    def process(danmu: Danmu):
        print("Receive danmu:", danmu.content)

    danmuReceiver.onReceive(process)
    await danmuReceiver.startReceive()


async def testReplyDanmu():
    chater: BaseChatter = componentManager.buildChatter(birespiConfig["chatter"])
    speaker: BaseSpeaker = componentManager.buildSpeaker(birespiConfig["speaker"])
    player: BasePlayer = componentManager.buildPlayer(birespiConfig["player"])
    danmuReceiver: BaseDanmuReceiver = componentManager.buildDanmuReceiver(
        birespiConfig["danmu_receiver"]
    )
    fastConsumptionQueue = FastConsumptionQueue[Danmu]()

    def process(danmu: Danmu):
        print("Receive danmu:", danmu.username, ": ", danmu.content)
        fastConsumptionQueue.push(danmu)

    async def response():
        playLock = Lock()
        while True:
            danmu: Optional[Danmu] = fastConsumptionQueue.pop()
            if danmu == None:
                print("没获取到弹幕,等待...")
                await asyncio.sleep(1)
                continue
            print("Pop danmu:", danmu)

            with playLock:
                if danmu:
                    answer = await chater.answer(danmu.username + "说:" + danmu.content)
                    print("answer: ", answer)
                    sound = await speaker.speak(answer)
                    print("sound: ", sound)
                    player.play(sound)

            await asyncio.sleep(1)

    asyncio.create_task(response())

    async def wishes2Everyone():
        while True:
            fastConsumptionQueue.push(
                Danmu(
                    "w0fv1-dev",
                    "请你祝福直播间的所有人,祝福他们的事业和生活, 祝福他们的家人和朋友, 祝福他们的爱情和婚姻, 祝福他们的健康和快乐。",
                )
            )
            await asyncio.sleep(10)

    asyncio.create_task(wishes2Everyone())

    danmuReceiver.onReceive(process)

    await danmuReceiver.startReceive()
