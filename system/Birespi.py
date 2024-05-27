import asyncio
from collections import deque
import threading
from typing import Optional
from model.ExportEvent import ExportEvent
from model.Task import Task, TaskType
from system.Logger import getLogger
from system.Config import getConfig
from model.LiveRoomInfo import LiveRoomInfo
from model.Talk import Talk
from system.TaskManager import TaskManager
from util.Queue import FastConsumptionQueue
from model.LiveEventMessage import LiveEvent, LiveMessage, DanmuMessageData
from system.ComponentManager import ComponentManager
from value.ComponentConfigKey import ComponentConfigKey


class Birespi:
    componentManager: ComponentManager = ComponentManager()

    taskManager: TaskManager = TaskManager()
    danmuDisplayqueue: deque[LiveMessage[DanmuMessageData]] = deque()
    lastTalk: tuple[Talk, Talk] = (None, None)
    liveRoomInfo: LiveRoomInfo = None

    def __init__(self) -> None:
        self.componentManager.loadComponents(getConfig().birespiConfig)
        self.componentManager.liveEventReceiver.onReceive(self.process)

    def reloadComponent(self, componentConfigKey: ComponentConfigKey):
        self.componentManager.putConfig(getConfig().birespiConfig)
        self.componentManager.build(componentConfigKey)

    def start(self) -> "Birespi":
        async def replyDanmu(danmuTask: Task[LiveMessage[DanmuMessageData]]):
            danmu: LiveMessage[DanmuMessageData] = danmuTask.taskData.getData()

            print(f"ReplyDanmu: {danmu}")
            data: str = await self.componentManager.dataer.getSimilarity(
                danmu.data.content
            )
            answer: str = await self.componentManager.chatter.answer(
                getConfig().getSystemPrompt(),
                f"""
你可以参考的数据是: {data}

当弹幕内容与数据无关时, 不要引用数据进行回答.
当弹幕内容与数据无关时, 不要引用数据进行回答.

-------

{danmu.fromUser} 说: "{danmu.data.content}".

请你回答弹幕
            """,
            )

            self.setLastTalk(danmu, answer)
            sound = await self.componentManager.speaker.speak(answer)
            exportEvent: ExportEvent = ExportEvent.Danmu(
                message=answer, sound=sound, liveMessage=danmu, task=danmuTask
            )
            await self.componentManager.eventExporter.send(exportEvent.toDict())
            self.componentManager.player.play(sound)

        async def execCommand(commandTask: Task[str]):
            command: str = commandTask.taskData.getData()

            print(f"command: {command}")
            data: str = await self.componentManager.dataer.getSimilarity(command)
            answer: str = await self.componentManager.chatter.answer(
                getConfig().getCommandPrompt(),
                f"""
你可以参考的数据是: {data}

你接受到的指令是: {command}

请你根据指令进行回答
            """,
            )
            sound = await self.componentManager.speaker.speak(answer)
            exportEvent: ExportEvent = ExportEvent.Command(
                message=answer, sound=sound, task=commandTask
            )
            await self.componentManager.eventExporter.send(exportEvent.toDict())
            self.componentManager.player.play(sound)

        self.taskManager.putWorkFuntion(TaskType.ReplyDanmu, replyDanmu)
        self.taskManager.putWorkFuntion(TaskType.ExecCommand, execCommand)
        thread = threading.Thread(target=self.startReceive)
        thread.start()

        thread = threading.Thread(target=self.startWork)
        thread.start()
        print("Birespi word started")
        serverThread = threading.Thread(target=self.startEventExporter)
        serverThread.start()

        print("Birespi EventExporter started")
        return self

    async def replyByBid(self, bId: str):
        danmu: LiveMessage[DanmuMessageData] = None
        for d in self.danmuDisplayqueue:
            if d.bId == bId:
                danmu = d
                break
        if danmu != None:
            await self.taskManager.addTask(Task.ReplyDanmu(danmu))

    def startReceive(self):
        asyncio.run(self.componentManager.liveEventReceiver.startReceive())

    def startWork(self):
        asyncio.run(self.taskManager.start())

    def startEventExporter(self):
        serverThread = threading.Thread(target=self.componentManager.eventExporter.startSoundFileApi)
        serverThread.start()
        asyncio.run(self.componentManager.eventExporter.start())
        

    def process(self, danmu: LiveMessage):
        if danmu.event == LiveEvent.Danmu:
            self.insertDanmu(danmu)

    def insertDanmu(self, danmu: LiveMessage[DanmuMessageData]):
        self.taskManager.addTask(Task.ReplyDanmu(danmu))
        self.danmuDisplayqueue.append(danmu)
        if len(self.danmuDisplayqueue) > 100:
            self.danmuDisplayqueue.popleft()

    def getDanmus(self) -> deque[LiveMessage[DanmuMessageData]]:
        return self.danmuDisplayqueue

    def setLastTalk(self, talk: LiveMessage[DanmuMessageData], answer: str):
        self.lastTalk = (Talk.fromDanmu(talk), Talk.fromBirespi(answer))

    def getLastTalk(self) -> tuple[Talk, Talk]:
        return self.lastTalk

    def getLiveRoomInfo(self) -> LiveRoomInfo:
        return self.componentManager.liveEventReceiver.getLiveRoomInfo()

    def getComponentManager(self) -> ComponentManager:
        return self.componentManager

    def getDataFiles(self) -> list[str]:
        return self.componentManager.dataer.getDataFiles()

    def getData(self, filename: str) -> str:
        return self.componentManager.dataer.getData(filename)

    def updateData(self, filename: str, content: str):
        self.componentManager.dataer.updateData(filename, content)

    def uploadData(self, filename: str, content: str):
        self.componentManager.dataer.uploadData(filename, content)

    def deleteData(self, filename: str):
        self.componentManager.dataer.deleteData(filename)

    def getCurrentTask(self) -> Optional[Task]:
        return self.taskManager.getCurrentTask()

    def getAllTasks(self) -> list[Task]:
        return self.taskManager.getAllTasks()

    def getTaskManagerInfo(self) -> dict:
        return self.taskManager.getInfo()

    def setTaskManagerPaused(self, paused: bool):
        self.taskManager.setPaused(paused)

    def addCommandTask(self, command: str):
        self.taskManager.addTask(Task.Command(command))


class BirespiHolder:
    birespi: Birespi = None

    def set(self, birespi: Birespi):
        self.birespi = birespi

    def get(self) -> Birespi:
        return self.birespi


biRespiHolder: BirespiHolder = BirespiHolder()


def getBirespi() -> Birespi:
    return biRespiHolder.get()
