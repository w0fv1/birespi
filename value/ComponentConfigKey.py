from enum import Enum

class ComponentConfigKey(Enum):
    Chatter = "chatter"
    Speaker = "speaker"
    Player = "player"
    DanmuReceiver = "danmu_receiver"
    WebUi = "web_ui"

    def __str__(self) -> str:
        return self.value

    def fromStr(str: str) -> "ComponentConfigKey":
        if str == "chatter":
            return ComponentConfigKey.Chatter
        elif str == "speaker":
            return ComponentConfigKey.Speaker
        elif str == "player":
            return ComponentConfigKey.Player
        elif str == "danmu_receiver":
            return ComponentConfigKey.DanmuReceiver
        elif str == "web_ui":
            return ComponentConfigKey.WebUi
        else:
            raise Exception(f"Unknown component key {str}")