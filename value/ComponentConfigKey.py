from enum import Enum


class ComponentConfigKey(Enum):
    Chatter = "chatter"
    Speaker = "speaker"
    Player = "player"
    LiveEventReceiver = "live_event_receiver"
    WebUi = "web_ui"
    Logger = "logger"
    Dataer = "dataer"
    EventExporter = "event_exporter"

    def __str__(self) -> str:
        return self.value

    def fromStr(str: str) -> "ComponentConfigKey":
        if type(str) == ComponentConfigKey:
            return str
        if str == "chatter":
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
        elif str == "dataer":
            return ComponentConfigKey.Dataer
        elif str == "event_exporter":
            return ComponentConfigKey.EventExporter
        else:
            raise Exception(f"Unknown component key |{str}|")
