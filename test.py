import asyncio
from typing import Optional
from component.LiveEventReceiver import (
    BaseLiveEventReceiver,
    BiliOpenLiveEventReceiver,
)
from component.Chatter import BaseChatter
from util.Queue import FastConsumptionQueue
from component.SoundPlayer import BasePlayer
from component.Speaker import BaseSpeaker
from config import BiRespiConfig
from model.LiveEventMessage import Danmu
import threading
from threading import Lock
from system.ComponentManager import ComponentManager
import os

birespiConfig = BiRespiConfig.birespiConfig
componentManager = ComponentManager()
componentManager.loadComponents(birespiConfig)



async def testChatter():
    chater: BaseChatter = componentManager.buildChatter(birespiConfig["chatter"])
    result = await chater.answer("Hello")
    


async def testSpeaker():
    speaker: BaseSpeaker = componentManager.buildSpeaker(birespiConfig["speaker"])
    result = await speaker.speak("你好")
    


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
    
    result = await speaker.speak(result)
    
    player.play(result)


async def testLiveEventReceiver():
    LiveEventReceiver: BaseLiveEventReceiver = componentManager.buildLiveEventReceiver(
        birespiConfig["live_event_receiver"]
    )

    def process(danmu: Danmu):
        

    LiveEventReceiver.onReceive(process)
    await LiveEventReceiver.startReceive()


async def testReplyDanmu():
    chater: BaseChatter = componentManager.buildChatter(birespiConfig["chatter"])
    speaker: BaseSpeaker = componentManager.buildSpeaker(birespiConfig["speaker"])
    player: BasePlayer = componentManager.buildPlayer(birespiConfig["player"])
    LiveEventReceiver: BaseLiveEventReceiver = componentManager.buildLiveEventReceiver(
        birespiConfig["live_event_receiver"]
    )
    fastConsumptionQueue = FastConsumptionQueue[Danmu]()

    def process(danmu: Danmu):
        
        fastConsumptionQueue.push(danmu)

    async def response():
        playLock = Lock()
        while True:
            danmu: Optional[Danmu] = fastConsumptionQueue.pop()
            if danmu == None:
                
                await asyncio.sleep(1)
                continue
            

            with playLock:
                if danmu:
                    answer = await chater.answer(danmu.username + "说:" + danmu.content)
                    
                    sound = await speaker.speak(answer)
                    
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

    LiveEventReceiver.onReceive(process)

    await LiveEventReceiver.startReceive()
