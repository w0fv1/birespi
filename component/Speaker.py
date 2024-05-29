import asyncio
import time
import random
import string
import edge_tts
import os

from component.BaseConfig import BaseConfig


class BaseSpeaker:
    async def speak(self, content: str) -> str:
        raise NotImplementedError


class EdgeSpeakerConfig(BaseConfig):

    voice: str
    outputPath: str

    def __init__(self, voice: str, outputPath: str) -> None:
        self.voice = voice
        self.outputPath = outputPath

    @staticmethod
    def fromJson(json: dict):
        return EdgeSpeakerConfig(
            voice=json["voice"],
            outputPath=json["outputPath"],
        )

class EdgeSpeaker(BaseSpeaker):
    config: EdgeSpeakerConfig = None

    def __init__(self, configDict: dict) -> None:
        super().__init__()
        self.config = EdgeSpeakerConfig.fromJson(configDict)
        self.deleteExpired()

    async def speak(self, content: str) -> str:
        if not os.path.exists(self.config.outputPath):
            os.makedirs(self.config.outputPath)
        # 获取随机uuid
        uuid = "".join(random.sample(string.ascii_letters + string.digits, 8))
        output_file = os.path.join(self.config.outputPath, f"{uuid}.mp3")
        communicate = edge_tts.Communicate(content, self.config.voice)
        await communicate.save(output_file)
        return output_file

    def deleteExpired(self):
        # 删除超过一天时间的过期文件
        for file in os.listdir(self.config.outputPath):
            file_path = os.path.join(self.config.outputPath, file)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < time.time() - 24 * 60 * 60:
                    os.remove(file_path)