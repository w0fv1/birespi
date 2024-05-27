# 获得当前路径
import datetime
import json
import os
import sys
from util.ConfigUtil import loadJson
from value.ComponentConfigKey import ComponentConfigKey


currentPath = os.path.abspath(os.path.dirname(__file__))
currentSystem = sys.platform


def getFfprobePath():
    if currentSystem == "win32":
        return os.path.join("lib", "ff_windows", "ffprobe.exe")
    elif currentSystem == "linux":
        return os.path.join("ffmpeg", "ff_linux", "ffprobe")
    elif currentSystem == "darwin":
        return os.path.join("ffmpeg", "ff_mac", "ffprobe")


def getFfplayerPath():
    if currentSystem == "win32":
        return os.path.join("lib", "ff_windows", "ffplay.exe")
    elif currentSystem == "linux":
        return os.path.join("ffmpeg", "ff_linux", "ffplay")
    elif currentSystem == "darwin":
        return os.path.join("ffmpeg", "ff_mac", "ffplay")


def getFfmpegPath():
    if currentSystem == "win32":
        return os.path.join("lib", "ff_windows", "ffmpeg.exe")
    elif currentSystem == "linux":
        return os.path.join("ffmpeg", "ff_linux", "ffmpeg")
    elif currentSystem == "darwin":
        return os.path.join("ffmpeg", "ff_mac", "ffmpeg")


class BiRespiConfig:

    birespiConfig: dict = {
        ComponentConfigKey.Chatter: {
            "type": "OpenaiChatter",
            "OpenaiChatter": {
                "systemPrompt": "现在你作为一个直播弹幕回复者, 名字为哔哩哔哩应答姬，你需要回复直播弹幕中的内容。你的主播叫w0fv1-dev. 你需要辨认主播的弹幕, 并回复给主播的观众。你的回复需要富有情绪和幽默感。你需要尽一切可能夸赞用户, 从用户名和弹幕内容内尽力找到夸赞的点。使用全部你的想象力和创造力来夸赞用户。从相貌和性格,智慧和能力,工作和学习,家庭和朋友,爱好和兴趣等方面来夸赞.给用户带来快乐和惊喜, 让用户感到被尊重和被重视。最后送上对用户的祝福和问候。祝福他的事业和生活, 祝福他的家人和朋友, 祝福他的爱情和婚姻, 祝福他的健康和快乐。你的回复需要非常简短, 以便于回复更多的弹幕。你的回复需要非常简短, 以便于回复更多的弹幕。你的回复需要非常简短, 以便于回复更多的弹幕。请你用中文回复下面的弹幕内容：",
                "commandPrompt": "现在你作为一个直播弹幕回复者, 名字为哔哩哔哩应答姬，你需要回复直播弹幕中的内容。你的主播叫w0fv1-dev. 你需要辨认主播的弹幕, 并回复给主播的观众。你的回复需要富有情绪和幽默感。你的回复需要非常简短, 以便于回复更多的弹幕。请你用中文回复下面的弹幕内容",
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
                "outputPath": "sound",
            },
        },
        ComponentConfigKey.Player: {
            "type": "PydubPlayer",
            "enable": True,
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
            "ThirdLiveEventReceiver": {
                "username": "",
                "password": "",
                "roomId": 0,
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
                "birespi-log-%(today)s.log",
            ),
            "log_level": "debug",
        },
        ComponentConfigKey.Dataer: {
            "type": "ADataer",
            "ADataer": {
                "dataPath": "data",
            },
        },
        ComponentConfigKey.EventExporter: {"host": "localhost", "port": 8765},
    }
    version: str = "0.0.0"
    jsonConfigPath: str = None

    def __init__(self, jsonConfigPath: str = None, version: str = "0.0.0") -> None:
        if jsonConfigPath != None:

            self.loadJsonConfig(loadJson(jsonConfigPath))
        self.version = version
        self.jsonConfigPath = jsonConfigPath

    def __str__(self) -> str:
        return str(self.birespiConfig)

    def loadJsonConfig(self, jsonConfig: dict):

        for componentConfigKeyStr in jsonConfig.keys():
            componentConfig: dict = jsonConfig[componentConfigKeyStr]

            componentConfigKey: ComponentConfigKey = ComponentConfigKey.fromStr(
                componentConfigKeyStr
            )
            if "type" in componentConfig.keys():
                type = componentConfig["type"]
                self.birespiConfig[componentConfigKey]["type"] = type

            if "enable" in self.birespiConfig[componentConfigKey].keys():
                self.birespiConfig[componentConfigKey]["enable"] = componentConfig[
                    "enable"
                ]

            for subType in componentConfig.keys():
                if subType == "type":
                    continue
                self.setComponentConfig(
                    componentConfigKey, subType, componentConfig[subType]
                )

    def setComponentConfig(
        self, componentConfigKey: ComponentConfigKey, type: str, config: dict
    ):

        if componentConfigKey not in self.birespiConfig.keys():
            self.birespiConfig[componentConfigKey] = {}

        self.birespiConfig[componentConfigKey][type] = config

    def setComponentType(self, componentConfigKeyStr: str, type: str):
        componentConfigKey = ComponentConfigKey.fromStr(componentConfigKeyStr)
        self.birespiConfig[componentConfigKey]["type"] = type

    def getComponentKeys(self) -> list[ComponentConfigKey]:
        return list(self.birespiConfig.keys())

    def getComponentCurrentType(self, componentConfigKeyStr: str) -> str:
        componentConfigKey = ComponentConfigKey.fromStr(componentConfigKeyStr)
        component: dict = self.birespiConfig[componentConfigKey]
        if "type" not in component.keys():
            return ""
        return component["type"]

    def getComponentSubTypes(self, componentConfigKeyStr: str) -> list[str]:
        componentConfigKey = ComponentConfigKey.fromStr(componentConfigKeyStr)

        component: dict = self.birespiConfig[componentConfigKey]
        componentsSubTypes = list(component.keys())
        if "type" not in componentsSubTypes:
            return []
        componentsSubTypes.remove("type")
        return componentsSubTypes

    def getCurrentComponentConfig(self, componentConfigKeyStr: str) -> dict:
        componentConfigKey = ComponentConfigKey.fromStr(componentConfigKeyStr)
        if componentConfigKey == ComponentConfigKey.WebUi:
            return self.getWebUiConfigDict()
        if componentConfigKey == ComponentConfigKey.Logger:
            return self.getLoggerConfigDict()
        if componentConfigKey == ComponentConfigKey.LiveEventReceiver:
            return self.getEventExporterConfigDict()

        if "type" not in self.birespiConfig[componentConfigKey].keys():
            return self.birespiConfig[componentConfigKey]

        type = self.birespiConfig[componentConfigKey]["type"]

        return self.birespiConfig[componentConfigKey][type]

    def getComponentSubtypeConfig(
        self, componentConfigKeyStr: str, type: str = ""
    ) -> dict:
        componentConfigKey = ComponentConfigKey.fromStr(componentConfigKeyStr)
        if componentConfigKey == ComponentConfigKey.WebUi:
            return self.getWebUiConfigDict()
        if componentConfigKey == ComponentConfigKey.Logger:
            return self.getLoggerConfigDict()
        if componentConfigKey == ComponentConfigKey.LiveEventReceiver:
            return self.getEventExporterConfigDict()

        if type == "":
            type = self.birespiConfig[componentConfigKey]

        return self.birespiConfig[componentConfigKey][type]

    def getWebUiConfigDict(self) -> dict:
        return self.birespiConfig[ComponentConfigKey.WebUi]

    def getLoggerConfigDict(self) -> dict:
        return self.birespiConfig[ComponentConfigKey.Logger]

    def getEventExporterConfigDict(self) -> dict:
        return self.birespiConfig[ComponentConfigKey.EventExporter]

    def getJsonConfig(self) -> dict:
        jsonConfig = {}
        for componentConfigKey in self.birespiConfig.keys():
            componentConfig = self.birespiConfig[componentConfigKey]
            if type(componentConfigKey) != ComponentConfigKey:
                raise Exception(
                    f"componentConfigKey {componentConfigKey} is not ComponentConfigKey"
                )

            jsonConfig[componentConfigKey.value] = componentConfig
        return json.dumps(jsonConfig, indent=4, ensure_ascii=False)

    def saveJsonConfig(self):
        # 获取原有的jsonConfig, 保存到bak文件夹, 以当前config-毫秒时间戳.json命名,如果没有bak文件夹,则创建

        if not os.path.exists("bak"):
            os.mkdir("bak")
        bakPath = os.path.join(
            "bak",
            f"config-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json.bak",
        )
        with open(bakPath, "w") as bakFile:
            # 获取现有的config.json文件
            with open(self.jsonConfigPath, "r") as jsonConfigFile:
                bakFile.write(jsonConfigFile.read())

        with open(self.jsonConfigPath, "w") as f:
            f.write(self.getJsonConfig())

    def getSystemPrompt(self) -> str:
        subtype: str = self.birespiConfig[ComponentConfigKey.Chatter]["type"]

        return self.birespiConfig[ComponentConfigKey.Chatter][subtype]["systemPrompt"]

    def getCommandPrompt(self) -> str:
        subtype: str = self.birespiConfig[ComponentConfigKey.Chatter]["type"]
        return self.birespiConfig[ComponentConfigKey.Chatter][subtype]["commandPrompt"]

    def enablePlayer(self) -> bool:
        return self.birespiConfig[ComponentConfigKey.Player]["enable"]


class BirespiConfigHolder:
    birespiConfig: BiRespiConfig = None

    def set(self, birespiConfig: BiRespiConfig):
        self.birespiConfig = birespiConfig

    def get(self) -> BiRespiConfig:
        return self.birespiConfig


birespiConfigHolder = BirespiConfigHolder()


def getConfig() -> BiRespiConfig:
    return birespiConfigHolder.get()
