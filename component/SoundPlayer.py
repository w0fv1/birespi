import winsound
from pydub import utils, AudioSegment
from pydub.playback import play

from component.BaseConfig import BaseConfig


class BasePlayer:
    def __init__(self):
        pass

    def play(self, sound: str):
        raise NotImplementedError


class WindowsPlayer(BasePlayer):
    def __init__(self):
        pass

    def play(self, sound: str):
        winsound.PlaySound(sound, winsound.SND_FILENAME)


class PydubPlayerConfig(BaseConfig):
    ffprobePath: str
    ffplayPath: str
    ffmpegPath: str

    def __init__(self, ffprobePath: str, ffplayPath: str, ffmpegPath: str):
        self.ffprobePath = ffprobePath
        self.ffplayPath = ffplayPath
        self.ffmpegPath = ffmpegPath

    @staticmethod
    def fromJson(json: dict):
        return PydubPlayerConfig(
            ffprobePath=json["ffprobePath"],
            ffplayPath=json["ffplayPath"],
            ffmpegPath=json["ffmpegPath"],
        )

    def notNone(self):
        return (
            self.ffprobePath != None
            and self.ffplayPath != None
            and self.ffmpegPath != None
        )


class PydubPlayer(BasePlayer):
    config: PydubPlayerConfig = None

    def __init__(self, configDict: dict):
        self.config = PydubPlayerConfig.fromJson(configDict)

    def play(self, sound: str):
        if self.config != None and self.config.notNone():

            def get_prober_name():
                return self.config.ffprobePath

            def get_player_name():
                return self.config.ffplayPath

            utils.get_prober_name = get_prober_name
            utils.get_player_name = get_player_name

            AudioSegment.ffmpeg = self.config.ffmpegPath
            AudioSegment.converter = self.config.ffmpegPath
        sound = AudioSegment.from_file(sound)
        play(sound)
