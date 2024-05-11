import winsound
import os
from pydub import utils, AudioSegment
from pydub.playback import play

from component.BaseConfig import BaseConfig

from subprocess import Popen
import miniaudio


class BasePlayer:
    def __init__(self):
        pass

    def play(self, soundPath: str):
        raise NotImplementedError


class WindowsPlayerConfig(BaseConfig):
    playDelete: bool = True

    def __init__(self, playDelete: bool = True):
        self.playDelete = playDelete

    def fromJson(json: dict):
        return WindowsPlayerConfig(playDelete=json["playDelete"])


class WindowsPlayer(BasePlayer):
    def __init__(self, configDict: dict):
        self.config = WindowsPlayerConfig.fromJson(configDict)

    def convert_mp3_to_wav(self, mp3_filename, wav_filename) -> str:
        # 解码MP3文件
        decoded_sound = miniaudio.decode_file(
            mp3_filename,
            output_format=miniaudio.SampleFormat.SIGNED16,
            nchannels=2,
            sample_rate=44100,
        )
        if self.config.playDelete:
            os.remove(mp3_filename)
        # 写入到WAV文件
        miniaudio.wav_write_file(wav_filename, decoded_sound)

        return wav_filename

    def play(self, soundPath: str):
        finalSoundPath = soundPath
        if soundPath.endswith(".mp3"):
            finalSoundPath = soundPath.replace(".mp3", ".wav")
            self.convert_mp3_to_wav(soundPath, finalSoundPath)
        if self.config.playDelete:
            os.remove(finalSoundPath)

        winsound.PlaySound(finalSoundPath, winsound.SND_FILENAME)


class MiniPlayer(BasePlayer):

    def __init__(self):
        pass

    def play(self, soundPath: str):
        stream = miniaudio.stream_file(soundPath)
        with miniaudio.PlaybackDevice() as device:
            device.start(stream)


class SubprocessPlayer(BasePlayer):
    def __init__(self):
        pass

    def play(self, soundPath: str):
        Popen(soundPath, shell=True)


class PydubPlayerConfig(BaseConfig):
    ffprobePath: str
    ffplayPath: str
    ffmpegPath: str
    playDelete: bool = True

    def __init__(
        self,
        ffprobePath: str,
        ffplayPath: str,
        ffmpegPath: str,
        playDelete: bool = True,
    ):
        self.ffprobePath = ffprobePath
        self.ffplayPath = ffplayPath
        self.ffmpegPath = ffmpegPath
        self.playDelete = playDelete

    @staticmethod
    def fromJson(json: dict):
        return PydubPlayerConfig(
            ffprobePath=json["ffprobePath"],
            ffplayPath=json["ffplayPath"],
            ffmpegPath=json["ffmpegPath"],
            playDelete=json["playDelete"],
        )

    def notNone(self):
        return (
            self.ffprobePath != None
            and self.ffplayPath != None
            and self.ffmpegPath != None
            and self.playDelete != None
        )


class PydubPlayer(BasePlayer):
    config: PydubPlayerConfig = None

    def __init__(self, configDict: dict):
        self.config = PydubPlayerConfig.fromJson(configDict)

    def play(self, soundPath: str):
        if self.config != None and self.config.notNone():

            def get_prober_name():
                return self.config.ffprobePath

            def get_player_name():
                return self.config.ffplayPath

            utils.get_prober_name = get_prober_name
            utils.get_player_name = get_player_name

            AudioSegment.ffmpeg = self.config.ffmpegPath
            AudioSegment.converter = self.config.ffmpegPath
        sound = AudioSegment.from_file(soundPath)
        play(sound)
        if self.config.playDelete:
            # 调用系统命令删除文件sound
            os.remove(soundPath)
