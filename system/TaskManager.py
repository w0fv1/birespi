import asyncio
from collections import deque
from typing import Callable, Dict

from model.Task import TaskType, Task
from system.Logger import getLogger


class TaskManager:
    taskQueue: deque = deque[Task]()
    isWorking: bool = False
    workFunctionMap: Dict[TaskType, Callable[[Task], None]] = {}

    currentTask: Task = None

    def __init__(self):
        pass

    def addTask(self, task: Task):
        insertIndex = len(self.taskQueue)
        for i in range(len(self.taskQueue)):
            if self.taskQueue[i].priority < task.priority:
                insertIndex = i

        try:
            self.taskQueue.insert(insertIndex, task)
        except Exception as e:
            getLogger().logError(
                f"TaskManager: Failed to insert task into taskQueue: {e}"
            )
            if len(self.taskQueue) == 0:
                self.taskQueue.append(task)
            else:
                if task.priority > 5:
                    self.taskQueue.insert(0, task)

        getLogger().logInfo(f"TaskManager: Task added, taskType: {task.taskType}")

    def getTask(self):
        return self.taskQueue.popleft()

    def putWorkFuntion(self, taskType: TaskType, workFunction: Callable[[Task], None]):
        self.workFunctionMap[taskType] = workFunction

    async def start(self):
        getLogger().logInfo("TaskManager started")
        while True:
            if len(self.taskQueue) == 0:
                getLogger().logInfo("TaskManager: No task to process")
                await asyncio.sleep(1)
                continue
            if self.isWorking:
                getLogger().logWarning("TaskManager: TaskManager is working")
                await asyncio.sleep(1)
                continue
            getLogger().logInfo("TaskManager: Getting task")
            task = self.getTask()
            await self.process(task)

            pass

    async def process(self, task: Task):
        getLogger().logInfo(f"TaskManager: Processing task, taskType: {task.taskType}")
        if self.isWorking:
            getLogger().logWarning(
                "TaskManager: TaskManager is working, cannot process task"
            )
            return
        self.isWorking = True
        self.currentTask = task
        print(f"TaskManager: Processing task, self currentTask: {self.currentTask}")


        workFunction = self.workFunctionMap.get(task.taskType)
        if workFunction is not None:
            getLogger().logInfo(
                f"TaskManager: Processing task, taskType: {task.taskType} with work function {workFunction}"
            )
            await workFunction(task)
        else:
            getLogger().logWarning(
                f"TaskManager: No work function for task type {task.taskType}"
            )
        self.isWorking = False

    def getCurrentTask(self):
        return self.currentTask

    def getAllTasks(self):
        return list(self.taskQueue)
