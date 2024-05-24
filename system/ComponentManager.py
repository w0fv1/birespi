from component.Chatter import BaseChatter, OpenaiChatter, WebChatter
from component.LiveEventReceiver import (
    BaseLiveEventReceiver,
    BiliOpenLiveEventReceiver,
    ThirdLiveEventReceiver,
)
from component.SoundPlayer import (
    BasePlayer,
    MiniPlayer,
    PydubPlayer,
    SubprocessPlayer,
    WindowsPlayer,
)
from component.Speaker import BaseSpeaker, EdgeSpeaker
from value.ComponentConfigKey import ComponentConfigKey
from component.Dataer import BaseDataer, ADataer


class ComponentManager:

    config: dict = {}

    chatter: BaseChatter = BaseChatter()
    LiveEventReceiver: BaseLiveEventReceiver = BaseLiveEventReceiver()
    player: BasePlayer = BasePlayer()
    speaker: BaseSpeaker = BaseSpeaker()
    dataer: BaseDataer = BaseDataer()

    def loadComponents(self, config: dict):
        self.config = config
        for key in config:
            self.build(key)

    def putConfig(self, config: dict):
        self.config = config

    def build(self, key: ComponentConfigKey):

        if key == ComponentConfigKey.Chatter:
            self.chatter = self.buildChatter(self.config[key])
        elif key == ComponentConfigKey.LiveEventReceiver:
            self.LiveEventReceiver = self.buildLiveEventReceiver(self.config[key])
        elif key == ComponentConfigKey.Player:
            self.player = self.buildPlayer(self.config[key])
        elif key == ComponentConfigKey.Speaker:
            self.speaker = self.buildSpeaker(self.config[key])
        elif key == ComponentConfigKey.Dataer:
            self.dataer = self.buildDataer(self.config[key])
        elif key == ComponentConfigKey.WebUi:
            pass
        elif key == ComponentConfigKey.Logger:
            pass
        else:
            raise Exception(f"Unknown component type {key}")

    def buildChatter(self, config: dict) -> BaseChatter:
        if config["type"] == "OpenaiChatter":
            return OpenaiChatter(config[config["type"]])
        elif config["type"] == "WebChatter":
            return WebChatter(config[config["type"]])
        else:
            raise Exception("Unknown chatter type")

    def buildLiveEventReceiver(self, config: dict) -> BaseLiveEventReceiver:
        if config["type"] == "BiliOpenLiveEventReceiver":
            return BiliOpenLiveEventReceiver(config[config["type"]])
        elif config["type"] == "ThirdLiveEventReceiver":
            return ThirdLiveEventReceiver(config[config["type"]])
        else:
            raise Exception("不支持的弹幕接收器类型")

    def buildPlayer(self, config: dict) -> BasePlayer:
        if config["type"] == "WindowsPlayer":
            return WindowsPlayer(config[config["type"]])
        elif config["type"] == "PydubPlayer":
            return PydubPlayer(config[config["type"]])
        elif config["type"] == "SubprocessPlayer":
            return SubprocessPlayer()
        elif config["type"] == "MiniPlayer":
            return MiniPlayer(config[config["type"]])
        else:
            raise NotImplementedError

    def buildSpeaker(self, config) -> BaseSpeaker:
        if config["type"] == "EdgeSpeaker":
            return EdgeSpeaker(config[config["type"]])
        else:
            raise Exception("Not support type")

    def buildDataer(self, config) -> BaseDataer:
        if config["type"] == "ADataer":
            return ADataer(config[config["type"]])
        else:
            raise Exception("Not support type")
