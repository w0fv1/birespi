from component.Chatter import BaseChatter, OpenaiChatter, WebChatter
from component.DanmuReceiver import BaseDanmuReceiver, BiliOpenDanmuReceiver
from component.SoundPlayer import BasePlayer, MiniPlayer, PydubPlayer, SubprocessPlayer, WindowsPlayer
from component.Speaker import BaseSpeaker, EdgeSpeaker
from value.ComponentConfigKey import ComponentConfigKey


class ComponentManager:

    config: dict = {}

    chatter: BaseChatter = BaseChatter()
    danmuReceiver: BaseDanmuReceiver = BaseDanmuReceiver()
    player: BasePlayer = BasePlayer()
    speaker: BaseSpeaker = BaseSpeaker()

    def loadComponents(self, config: dict):
        self.config = config
        for key in config:
            self.build(key)

    def putConfig(self, key: str, config: dict):
        self.config[key] = config
        self.build(key)

    def build(self, key: ComponentConfigKey):
        print("Build component key: ", key)
        print("Build component key: ", type(key))
        print("Build component config: ", self.config[key])

        if key == ComponentConfigKey.Chatter:
            self.chatter = self.buildChatter(self.config[key])
        elif key == ComponentConfigKey.DanmuReceiver:
            self.danmuReceiver = self.buildDanmuReceiver(self.config[key])
        elif key == ComponentConfigKey.Player:
            self.player = self.buildPlayer(self.config[key])
        elif key == ComponentConfigKey.Speaker:
            self.speaker = self.buildSpeaker(self.config[key])
        elif key == ComponentConfigKey.WebUi:
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

    def buildDanmuReceiver(self, config: dict) -> BaseDanmuReceiver:
        if config["type"] == "BiliOpenDanmuReceiver":
            return BiliOpenDanmuReceiver(config[config["type"]])
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
