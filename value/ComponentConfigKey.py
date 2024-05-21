from enum import Enum


class ComponentConfigKey(Enum):
    Chatter = "chatter"
    Speaker = "speaker"
    Player = "player"
    LiveEventReceiver = "live_event_receiver"
    WebUi = "web_ui"
    Logger = "logger"

    def __str__(self) -> str:
        return self.value

    def fromStr(str: str) -> "ComponentConfigKey":
        print(f"strstrstrstrstr '{str}' == 'chatter' {str == "chatter"}",str)
        if str == "chatter":
            print("chatterchatterchatter ComponentConfigKey.Chatter",ComponentConfigKey.Chatter)
            return ComponentConfigKey.Chatter
        elif str == "speaker":
            return ComponentConfigKey.Speaker
        elif str == "player":
            return ComponentConfigKey.Player
        elif str == "live_event_receiver":
            return ComponentConfigKey.LiveEventReceiver
        elif str == "web_ui":
            return ComponentConfigKey.WebUi
        elif str == "logger":
            return ComponentConfigKey.Logger
        else:
            print("chatterchatterchatter ComponentConfigKey.Chatter",ComponentConfigKey.Chatter)
            print("strstrstrstrstr str == 'chatter'",str == "chatter")
            raise Exception(f"Unknown component key |{str}|")
