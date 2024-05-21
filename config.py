# 获得当前路径
import datetime
import os
import sys
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
        ComponentConfigKey.LiveEventReceiver: {
            "type": "BiliOpenLiveEventReceiver",
            "BiliOpenLiveEventReceiver": {
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
        ComponentConfigKey.Logger: {
            "formatter": "[%(asctime)s]-[%(name)s-%(levelname)s]-%(funcName)s(): %(message)s",
            "filename": os.path.join(
                f"log",
                f'birespi-log-{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
            ),
            "log_level": "debug",
        },
    }
    version: str = "0.0.0"

    def __init__(self, jsonConfigPath: str = None, version: str = "0.0.0") -> None:
        if jsonConfigPath != None:

            self.loadJsonConfig(loadJson(jsonConfigPath))
        self.version = version

    def __str__(self) -> str:
        return str(self.birespiConfig)

    def setComponentConfig(self, componentConfigKeyStr: str, type: str, config: dict):

        componentConfigKey: ComponentConfigKey = ComponentConfigKey.fromStr(
            componentConfigKeyStr
        )

        if componentConfigKey not in self.birespiConfig.keys():
            self.birespiConfig[componentConfigKey] = {}

        if (
            componentConfigKey == ComponentConfigKey.WebUi
            or componentConfigKey == ComponentConfigKey.Logger
        ):
            self.birespiConfig[componentConfigKey] = config
            return

        self.birespiConfig[componentConfigKey][type] = config

    def loadJsonConfig(self, jsonConfig: dict):

        for componentConfigKey in jsonConfig.keys():
            componentConfig: dict = jsonConfig[componentConfigKey]

            type = ""
            if "type" in componentConfig.keys():
                type = componentConfig["type"]

            config = componentConfig
            if "type" in componentConfig.keys():
                config = componentConfig[type]
            self.setComponentConfig(
                componentConfigKey,
                type,
                config,
            )

    def getComponents(self) -> list[ComponentConfigKey]:
        return list(self.birespiConfig.keys())

    def getComponentSubTypes(self, componentConfigKey: ComponentConfigKey) -> list[str]:
        component: dict = self.birespiConfig[componentConfigKey]
        componentsSubTypes = list(component.keys())
        if "type" not in componentsSubTypes:
            raise Exception("不是有子类别的组件")
        componentsSubTypes.remove("type")
        return componentsSubTypes

    def getComponentConfigDict(
        self, componentConfigKey: ComponentConfigKey, subType: str = None
    ) -> dict:
        if componentConfigKey == ComponentConfigKey.WebUi:
            return self.getWebUiConfigDict()
        if componentConfigKey == ComponentConfigKey.Logger:
            return self.getLoggerConfigDict()

        return self.birespiConfig[componentConfigKey][subType]

    def getWebUiConfigDict(self) -> dict:
        return self.birespiConfig[ComponentConfigKey.WebUi]

    def getLoggerConfigDict(self) -> dict:
        return self.birespiConfig[ComponentConfigKey.Logger]


class BirespiConfigHolder:
    birespiConfig: BiRespiConfig = None

    def set(self, birespiConfig: BiRespiConfig):
        self.birespiConfig = birespiConfig

    def get(self) -> BiRespiConfig:
        return self.birespiConfig


birespiConfigHolder = BirespiConfigHolder()


def getConfig() -> BiRespiConfig:
    return birespiConfigHolder.get()
