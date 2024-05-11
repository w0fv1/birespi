# import asyncio
# from Birespi import Birespi
# from config import BiRespiConfig
# from util.ConfigUtil import argDict, getConfigPath, loadJson

# configPath = getConfigPath()

# print("configPath:", configPath)

# async def startBirespi():
#     await Birespi(
#         BiRespiConfig(jsonConfigPath=loadJson(configPath)).birespiConfig
#     ).startRespi()

#     # 这里假设 main 中有持续运行的任务
#     while True:
#         await asyncio.sleep(10)


# if __name__ == "__main__":
#     asyncio.run(startBirespi())

import numpy as np
from scipy.io import wavfile
import wave

def mp3_to_wav(source_path, target_path):
    # 读取 MP3 文件
    rate, data = wavfile.read(source_path)  # 这里假设 scipy 可以直接读取 MP3，实际可能需要额外的处理
    # 将数据转为 wav 格式并保存
    with wave.open(target_path, 'w') as wav_file:
        wav_file.setnchannels(1 if data.ndim == 1 else data.shape[1])
        wav_file.setsampwidth(np.iinfo(data.dtype).bits // 8)
        wav_file.setframerate(rate)
        wav_file.writeframes(data.tobytes())

# 使用示例
mp3_to_wav('path_to_your_mp3_file.mp3', 'output_file.wav')

