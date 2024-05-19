# 获得当前路径
import os
import sys

from component.Chatter import OpenaiChatterConfig
from component.DanmuReceiver import BiliOpenDanmuReceiverConfig
from component.SoundPlayer import PydubPlayerConfig
from component.Speaker import EdgeSpeakerConfig
from util.ConfigUtil import loadJson
from value.ComponentConfigKey import ComponentConfigKey


currentPath = os.path.abspath(os.path.dirname(__file__))
currentSystem = sys.platform


def getFfprobePath():
    if currentSystem == "win32":
        return os.path.join(currentPath, "lib", "ff_windows", "ffprobe.exe")
    elif currentSystem == "linux":
        return os.path.join(currentPath, "ffmpeg", "ff_linux", "ffprobe")
    elif currentSystem == "darwin":
        return os.path.join(currentPath, "ffmpeg", "ff_mac", "ffprobe")


def getFfplayerPath():
    if currentSystem == "win32":
        return os.path.join(currentPath, "lib", "ff_windows", "ffplay.exe")
    elif currentSystem == "linux":
        return os.path.join(currentPath, "ffmpeg", "ff_linux", "ffplay")
    elif currentSystem == "darwin":
        return os.path.join(currentPath, "ffmpeg", "ff_mac", "ffplay")


def getFfmpegPath():
    if currentSystem == "win32":
        return os.path.join(currentPath, "lib", "ff_windows", "ffmpeg.exe")
    elif currentSystem == "linux":
        return os.path.join(currentPath, "ffmpeg", "ff_linux", "ffmpeg")
    elif currentSystem == "darwin":
        return os.path.join(currentPath, "ffmpeg", "ff_mac", "ffmpeg")


class BiRespiConfig:

    birespiConfig: dict = {
        ComponentConfigKey.Chatter: {
            "type": "OpenaiChatter",
            "OpenaiChatter": {
                "systemPrompt": "现在你作为一个直播弹幕回复者, 名字为哔哩哔哩应答姬，你需要回复直播弹幕中的内容。你的主播叫w0fv1-dev. 你需要辨认主播的弹幕, 并回复给主播的观众。你的回复需要富有情绪和幽默感。你需要尽一切可能夸赞用户, 从用户名和弹幕内容内尽力找到夸赞的点。使用全部你的想象力和创造力来夸赞用户。从相貌和性格,智慧和能力,工作和学习,家庭和朋友,爱好和兴趣等方面来夸赞.给用户带来快乐和惊喜, 让用户感到被尊重和被重视。最后送上对用户的祝福和问候。祝福他的事业和生活, 祝福他的家人和朋友, 祝福他的爱情和婚姻, 祝福他的健康和快乐。你的回复需要非常简短, 以便于回复更多的弹幕。你的回复需要非常简短, 以便于回复更多的弹幕。你的回复需要非常简短, 以便于回复更多的弹幕。请你用中文回复下面的弹幕内容：",
                "apiKey": "",
                "host": "https://api.deepseek.com",
                "model": "deepseek-chat",
                "temperature": 1.2,
            },
        },
        ComponentConfigKey.Speaker: {
            "type": "EdgeSpeaker",
            "EdgeSpeaker": {
                "voice": "zh-CN-XiaoxiaoNeural",
                "outputPath": os.path.join(currentPath, "sound"),
            },
        },
        ComponentConfigKey.Player: {
            "type": "PydubPlayer",
            "PydubPlayer": {
                "ffprobePath": getFfprobePath(),
                "ffplayPath": getFfplayerPath(),
                "ffmpegPath": getFfmpegPath(),
                "playDelete": True,
            },
            "SubprocessPlayer": {
                "playDelete": True,
            },
            "WindowsPlayer": {
                "playDelete": True,
            },
            "MiniPlayer": {"playDelete": True},
        },
        ComponentConfigKey.DanmuReceiver: {
            "type": "BiliOpenDanmuReceiver",
            "BiliOpenDanmuReceiver": {
                "idCode": "",  # 主播身份码
                "appId": 0,  # 应用id
                "key": "",  # access_key
                "secret": "",  # access_key_secret
                "host": "",
            },
        },
        ComponentConfigKey.WebUi: {
            "username": "admin",
            "password": "admin",
            "port": 8000,
            "allowNoLocalhost": False,
        },
    }
    version: str = "0.0.0"

    def __init__(self, jsonConfigPath: str = None,version:str = "0.0.0") -> None:
        if jsonConfigPath != None:
            
            self.loadJsonConfig(loadJson(jsonConfigPath))
        self.version = version
    
    def __str__(self) -> str:
        return str(self.birespiConfig)

    def setComponentConfig(self, componentConfigKeyStr: str, type: str, config: dict):
        
        componentConfigKey:ComponentConfigKey = ComponentConfigKey.fromStr(componentConfigKeyStr)

        if componentConfigKey not in self.birespiConfig.keys():
            self.birespiConfig[componentConfigKey] = {}
        
        self.birespiConfig[componentConfigKey][type] = config

    def loadJsonConfig(self, jsonConfig: dict):
        
        for componentConfigKey in jsonConfig.keys():
            componentConfig: dict = jsonConfig[componentConfigKey]
            
            type = componentConfig["type"]
            self.setComponentConfig(
                componentConfigKey,
                type,
                componentConfig[type],
            )

    def getWebUiConfig(self):
        return self.birespiConfig[ComponentConfigKey.WebUi]
